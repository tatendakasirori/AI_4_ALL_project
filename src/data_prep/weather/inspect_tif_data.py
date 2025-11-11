import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np

# File path
tif_path = 'data/viirs_data/NJ/NJ_2021-03-01.tif'

def decode_cloud_mask(band3_data):
    """Decode QF_Cloud_Mask bitmask (Band 3)"""
    band3_int = band3_data.astype(np.uint16)
    results = {}
    
    # Bit 0: Day/Night
    results['is_day'] = (band3_int & 0b1).astype(bool)
    
    # Bits 1-3: Land/Water (0-7)
    results['land_water'] = (band3_int >> 1) & 0b111
    
    # Bits 4-5: Cloud Mask Quality (0-3)
    results['cloud_quality'] = (band3_int >> 4) & 0b11
    
    # Bits 6-7: Cloud Detection (0-3)
    results['cloud_confidence'] = (band3_int >> 6) & 0b11
    
    # Bit 8: Shadow
    results['shadow'] = ((band3_int >> 8) & 0b1).astype(bool)
    
    # Bit 9: Cirrus
    results['cirrus'] = ((band3_int >> 9) & 0b1).astype(bool)
    
    # Bit 10: Snow/Ice
    results['snow_ice'] = ((band3_int >> 10) & 0b1).astype(bool)
    
    return results

def interpret_quality_flag(band4_data):
    """Interpret Mandatory_Quality_Flag (Band 4)"""
    # Should be 0, 1, 2, or 255
    unique_vals = np.unique(band4_data)
    return unique_vals

with rasterio.open(tif_path) as src:
    # Basic metadata
    print("=== FILE METADATA ===")
    print(f"Driver: {src.driver}")
    print(f"Dimensions: {src.width} × {src.height} pixels")
    print(f"CRS: {src.crs}")
    print(f"Bounds: {src.bounds}")
    print(f"Number of bands: {src.count}\n")

    # Read all bands
    band1_lunar = src.read(1)
    band2_ntl = src.read(2)
    band3_cloudmask = src.read(3)
    band4_quality = src.read(4)
    
    # Band 1: Lunar Irradiance
    print("=== BAND 1: DNB_Lunar_Irradiance ===")
    print(f"Range: {np.nanmin(band1_lunar):.2f} - {np.nanmax(band1_lunar):.2f}")
    print(f"Mean: {np.nanmean(band1_lunar):.2f}")
    has_lunar = np.nanmax(band1_lunar) > 0
    print(f"Lunar data present: {has_lunar}")
    if has_lunar:
        print(f"  → Moon phase likely present (affects bird behavior)")
    else:
        print(f"  → New moon or data masked")
    print()
    
    # Band 2: Gap-Filled Nighttime Lights
    print("=== BAND 2: Gap_Filled_DNB_BRDF_Corrected_NTL ===")
    print(f"Range: {np.nanmin(band2_ntl):.2f} - {np.nanmax(band2_ntl):.2f} nW·cm⁻²·sr⁻¹")
    print(f"Mean: {np.nanmean(band2_ntl):.2f}")
    print(f"Median: {np.nanmedian(band2_ntl):.2f}")
    print(f"Std Dev: {np.nanstd(band2_ntl):.2f}")
    print(f"Non-zero pixels: {np.sum(band2_ntl > 0)} / {band2_ntl.size} ({100*np.sum(band2_ntl > 0)/band2_ntl.size:.1f}%)")
    print(f"  → PRIMARY PREDICTOR for light pollution analysis")
    print()
    
    # Band 3: Cloud Mask (decode bitmask)
    print("=== BAND 3: QF_Cloud_Mask (Bitmask) ===")
    decoded = decode_cloud_mask(band3_cloudmask)
    
    print(f"Day pixels: {np.sum(decoded['is_day'])} ({100*np.mean(decoded['is_day']):.1f}%)")
    print(f"Night pixels: {np.sum(~decoded['is_day'])} ({100*np.mean(~decoded['is_day']):.1f}%)")
    print()
    
    print("Cloud Detection Confidence:")
    cloud_conf = decoded['cloud_confidence']
    for val, label in [(0, 'Confident Clear'), (1, 'Probably Clear'), 
                        (2, 'Probably Cloudy'), (3, 'Confident Cloudy')]:
        count = np.sum(cloud_conf == val)
        pct = 100 * count / cloud_conf.size
        print(f"  {val} ({label}): {count} pixels ({pct:.1f}%)")
    
    print(f"\nSnow/Ice present: {np.sum(decoded['snow_ice'])} pixels ({100*np.mean(decoded['snow_ice']):.1f}%)")
    print(f"Shadow detected: {np.sum(decoded['shadow'])} pixels ({100*np.mean(decoded['shadow']):.1f}%)")
    print()
    
    # Calculate usable data percentage
    usable_mask = (cloud_conf <= 1) & (~decoded['snow_ice'])
    print(f"✓ USABLE PIXELS (clear + no snow): {np.sum(usable_mask)} ({100*np.mean(usable_mask):.1f}%)")
    print()
    
    # Band 4: Quality Flag
    print("=== BAND 4: Mandatory_Quality_Flag ===")
    unique_quality = interpret_quality_flag(band4_quality)
    print(f"Unique values: {unique_quality}")
    print(f"Range: {np.nanmin(band4_quality):.2f} - {np.nanmax(band4_quality):.2f}")
    print(f"Mean: {np.nanmean(band4_quality):.2f}")
    
    # Check if values are as expected (0, 1, 2, 255)
    expected_values = {0, 1, 2, 255}
    if not set(unique_quality).issubset(expected_values):
        print(f"⚠️  WARNING: Unexpected values detected!")
        print(f"   Expected: {expected_values}")
        print(f"   Got: {set(unique_quality)}")
        print(f"   → May indicate data corruption or unit conversion issue")
    else:
        for val in unique_quality:
            count = np.sum(band4_quality == val)
            pct = 100 * count / band4_quality.size
            label = {0: 'High-quality persistent', 1: 'High-quality ephemeral', 
                     2: 'Poor quality/cloud', 255: 'No retrieval'}[val]
            print(f"  {val} ({label}): {count} pixels ({pct:.1f}%)")
    print()
    
    # Data quality summary
    print("=== DATA QUALITY SUMMARY ===")
    ntl_valid = band2_ntl[usable_mask]
    print(f"After filtering (clear, no snow):")
    print(f"  Valid NTL pixels: {len(ntl_valid)}")
    print(f"  Mean light intensity: {np.mean(ntl_valid):.2f} nW·cm⁻²·sr⁻¹")
    print(f"  Coverage: {100*len(ntl_valid)/band2_ntl.size:.1f}% of total area")
    
    # Visualization
    fig = plt.figure(figsize=(16, 10))
    
    # Band 2: Nighttime Lights
    ax1 = plt.subplot(2, 3, 1)
    im1 = ax1.imshow(band2_ntl, cmap='hot', vmin=np.nanpercentile(band2_ntl, 2), 
                     vmax=np.nanpercentile(band2_ntl, 98))
    ax1.set_title('Band 2: Nighttime Lights\n(Primary Data)', fontweight='bold')
    ax1.axis('off')
    plt.colorbar(im1, ax=ax1, label='Radiance (nW·cm⁻²·sr⁻¹)')
    
    # Band 1: Lunar Irradiance
    ax2 = plt.subplot(2, 3, 2)
    im2 = ax2.imshow(band1_lunar, cmap='Blues')
    ax2.set_title('Band 1: Lunar Irradiance', fontweight='bold')
    ax2.axis('off')
    plt.colorbar(im2, ax=ax2, label='Lunar brightness')
    
    # Cloud confidence
    ax3 = plt.subplot(2, 3, 3)
    cloud_rgb = np.zeros((*cloud_conf.shape, 3))
    cloud_rgb[cloud_conf == 0] = [0, 1, 0]    # Green = clear
    cloud_rgb[cloud_conf == 1] = [0.5, 1, 0]  # Yellow-green = probably clear
    cloud_rgb[cloud_conf == 2] = [1, 0.5, 0]  # Orange = probably cloudy
    cloud_rgb[cloud_conf == 3] = [1, 0, 0]    # Red = cloudy
    ax3.imshow(cloud_rgb)
    ax3.set_title('Band 3: Cloud Confidence\n(Green=Clear, Red=Cloudy)', fontweight='bold')
    ax3.axis('off')
    
    # Snow/Ice mask
    ax4 = plt.subplot(2, 3, 4)
    ax4.imshow(decoded['snow_ice'], cmap='Blues')
    ax4.set_title('Band 3: Snow/Ice Flag', fontweight='bold')
    ax4.axis('off')
    
    # Usable data mask
    ax5 = plt.subplot(2, 3, 5)
    ax5.imshow(usable_mask, cmap='RdYlGn')
    ax5.set_title('Usable Pixels\n(Clear + No Snow)', fontweight='bold')
    ax5.axis('off')
    
    # Filtered nighttime lights
    ax6 = plt.subplot(2, 3, 6)
    filtered_ntl = band2_ntl.copy()
    filtered_ntl[~usable_mask] = np.nan
    im6 = ax6.imshow(filtered_ntl, cmap='hot', vmin=np.nanpercentile(filtered_ntl, 2), 
                     vmax=np.nanpercentile(filtered_ntl, 98))
    ax6.set_title('Filtered Nighttime Lights\n(Quality-Controlled)', fontweight='bold')
    ax6.axis('off')
    plt.colorbar(im6, ax=ax6, label='Radiance (nW·cm⁻²·sr⁻¹)')
    
    plt.tight_layout()
    plt.show()