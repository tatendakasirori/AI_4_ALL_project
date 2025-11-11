import rasterio
from rasterio.plot import show
import matplotlib.pyplot as plt
import numpy as np

# File path
tif_path = 'data/viirs_data/NJ/NJ_2021-03-01.tif'

def decode_cloud_mask(band7_data):
    """Decode QF_Cloud_Mask bitmask (Band 7)"""
    band7_int = band7_data.astype(np.uint16)
    results = {}
    
    # Bit 0: Day/Night
    results['is_day'] = (band7_int & 0b1).astype(bool)
    
    # Bits 1-3: Land/Water (0-7)
    results['land_water'] = (band7_int >> 1) & 0b111
    
    # Bits 4-5: Cloud Mask Quality (0-3)
    results['cloud_quality'] = (band7_int >> 4) & 0b11
    
    # Bits 6-7: Cloud Detection (0-3)
    results['cloud_confidence'] = (band7_int >> 6) & 0b11
    
    # Bit 8: Shadow
    results['shadow'] = ((band7_int >> 8) & 0b1).astype(bool)
    
    # Bit 9: Cirrus
    results['cirrus'] = ((band7_int >> 9) & 0b1).astype(bool)
    
    # Bit 10: Snow/Ice
    results['snow_ice'] = ((band7_int >> 10) & 0b1).astype(bool)
    
    return results

def interpret_quality_flag(band5_data):
    """Interpret Mandatory_Quality_Flag (Band 5)"""
    unique_vals = np.unique(band5_data)
    labels = {
        0: 'High-quality persistent',
        1: 'High-quality ephemeral',
        2: 'Poor quality/cloud contamination',
        3: 'Lunar eclipse',
        4: 'Aurora',
        5: 'Glint',
        255: 'No retrieval/Fill value'
    }
    return unique_vals, labels

with rasterio.open(tif_path) as src:
    # Basic metadata
    print("=" * 60)
    print("VIIRS VNP46A2 - Complete 7-Band Analysis")
    print("=" * 60)
    print(f"Driver: {src.driver}")
    print(f"Dimensions: {src.width} × {src.height} pixels")
    print(f"CRS: {src.crs}")
    print(f"Bounds: {src.bounds}")
    print(f"Number of bands: {src.count}")
    print(f"Resolution: 500m (0.004639° at equator)")
    print()

    # Read all 7 bands
    band1_ntl_brdf = src.read(1)           # DNB_BRDF_Corrected_NTL
    band2_ntl_gapfilled = src.read(2)      # Gap_Filled_DNB_BRDF_Corrected_NTL
    band3_lunar = src.read(3)              # DNB_Lunar_Irradiance
    band4_latest_hq = src.read(4)          # Latest_High_Quality_Retrieval
    band5_quality = src.read(5)            # Mandatory_Quality_Flag
    band6_snow = src.read(6)               # Snow_Flag
    band7_cloudmask = src.read(7)          # QF_Cloud_Mask
    
    # ========== BAND 1: DNB_BRDF_Corrected_NTL ==========
    print("=" * 60)
    print("BAND 1: DNB_BRDF_Corrected_NTL")
    print("=" * 60)
    print("Raw BRDF-corrected nighttime lights (may have gaps)")
    print(f"Range: {np.nanmin(band1_ntl_brdf):.2f} - {np.nanmax(band1_ntl_brdf):.2f} nW·cm⁻²·sr⁻¹")
    print(f"Mean: {np.nanmean(band1_ntl_brdf):.2f}")
    print(f"Median: {np.nanmedian(band1_ntl_brdf):.2f}")
    print(f"Non-zero pixels: {np.sum(band1_ntl_brdf > 0)} / {band1_ntl_brdf.size} ({100*np.sum(band1_ntl_brdf > 0)/band1_ntl_brdf.size:.1f}%)")
    print()
    
    # ========== BAND 2: Gap_Filled_DNB_BRDF_Corrected_NTL ==========
    print("=" * 60)
    print("BAND 2: Gap_Filled_DNB_BRDF_Corrected_NTL ⭐ PRIMARY")
    print("=" * 60)
    print("Gap-filled BRDF-corrected nighttime lights (BEST FOR ANALYSIS)")
    print(f"Range: {np.nanmin(band2_ntl_gapfilled):.2f} - {np.nanmax(band2_ntl_gapfilled):.2f} nW·cm⁻²·sr⁻¹")
    print(f"Mean: {np.nanmean(band2_ntl_gapfilled):.2f}")
    print(f"Median: {np.nanmedian(band2_ntl_gapfilled):.2f}")
    print(f"Std Dev: {np.nanstd(band2_ntl_gapfilled):.2f}")
    print(f"Non-zero pixels: {np.sum(band2_ntl_gapfilled > 0)} / {band2_ntl_gapfilled.size} ({100*np.sum(band2_ntl_gapfilled > 0)/band2_ntl_gapfilled.size:.1f}%)")
    print(f"→ Use this band for light pollution modeling")
    print()
    
    # ========== BAND 3: DNB_Lunar_Irradiance ==========
    print("=" * 60)
    print("BAND 3: DNB_Lunar_Irradiance")
    print("=" * 60)
    print("Moonlight contribution to nighttime brightness")
    print(f"Range: {np.nanmin(band3_lunar):.2f} - {np.nanmax(band3_lunar):.2f}")
    print(f"Mean: {np.nanmean(band3_lunar):.2f}")
    has_lunar = np.nanmax(band3_lunar) > 0
    print(f"Lunar data present: {has_lunar}")
    if has_lunar:
        print(f"→ Moon phase affects bird navigation behavior")
    else:
        print(f"→ New moon or data masked")
    print()
    
    # ========== BAND 4: Latest_High_Quality_Retrieval ==========
    print("=" * 60)
    print("BAND 4: Latest_High_Quality_Retrieval")
    print("=" * 60)
    print("Most recent high-quality observation (temporal tracking)")
    print(f"Range: {np.nanmin(band4_latest_hq):.2f} - {np.nanmax(band4_latest_hq):.2f}")
    print(f"Mean: {np.nanmean(band4_latest_hq):.2f}")
    print(f"Non-zero pixels: {np.sum(band4_latest_hq > 0)} ({100*np.sum(band4_latest_hq > 0)/band4_latest_hq.size:.1f}%)")
    print(f"→ Indicates data freshness/stability")
    print()
    
    # ========== BAND 5: Mandatory_Quality_Flag ==========
    print("=" * 60)
    print("BAND 5: Mandatory_Quality_Flag ⭐ CRITICAL FOR FILTERING")
    print("=" * 60)
    unique_quality, quality_labels = interpret_quality_flag(band5_quality)
    print(f"Unique values: {unique_quality}")
    
    for val in unique_quality:
        val_int = int(val)
        if val_int in quality_labels:
            count = np.sum(band5_quality == val)
            pct = 100 * count / band5_quality.size
            print(f"  {val_int:3d} ({quality_labels[val_int]}): {count:6d} pixels ({pct:5.1f}%)")
    
    # Calculate high-quality pixels
    hq_mask = (band5_quality == 0) | (band5_quality == 1)
    print(f"\n✓ HIGH-QUALITY pixels (0-1): {np.sum(hq_mask)} ({100*np.mean(hq_mask):.1f}%)")
    print()
    
    # ========== BAND 6: Snow_Flag ==========
    print("=" * 60)
    print("BAND 6: Snow_Flag")
    print("=" * 60)
    snow_present = np.sum(band6_snow == 1)
    snow_pct = 100 * snow_present / band6_snow.size
    print(f"No Snow/Ice (0): {np.sum(band6_snow == 0)} pixels ({100*np.sum(band6_snow == 0)/band6_snow.size:.1f}%)")
    print(f"Snow/Ice (1): {snow_present} pixels ({snow_pct:.1f}%)")
    if snow_pct > 5:
        print(f"⚠️  Significant snow cover detected - may affect light measurements")
    print()
    
    # ========== BAND 7: QF_Cloud_Mask (Bitmask) ==========
    print("=" * 60)
    print("BAND 7: QF_Cloud_Mask (Bitmask)")
    print("=" * 60)
    decoded = decode_cloud_mask(band7_cloudmask)
    
    print(f"Day pixels: {np.sum(decoded['is_day'])} ({100*np.mean(decoded['is_day']):.1f}%)")
    print(f"Night pixels: {np.sum(~decoded['is_day'])} ({100*np.mean(~decoded['is_day']):.1f}%)")
    print()
    
    print("Land/Water Classification:")
    landwater_labels = ['Land & Desert', 'Land no Desert', 'Inland Water', 
                        'Sea Water', 'Unknown', 'Coastal', 'Unknown', 'Unknown']
    for val in range(8):
        count = np.sum(decoded['land_water'] == val)
        if count > 0:
            pct = 100 * count / decoded['land_water'].size
            print(f"  {val} ({landwater_labels[val]}): {count} pixels ({pct:.1f}%)")
    print()
    
    print("Cloud Mask Quality:")
    for val, label in [(0, 'Poor'), (1, 'Low'), (2, 'Medium'), (3, 'High')]:
        count = np.sum(decoded['cloud_quality'] == val)
        pct = 100 * count / decoded['cloud_quality'].size
        print(f"  {val} ({label}): {count} pixels ({pct:.1f}%)")
    print()
    
    print("Cloud Detection Confidence:")
    cloud_conf = decoded['cloud_confidence']
    for val, label in [(0, 'Confident Clear'), (1, 'Probably Clear'), 
                        (2, 'Probably Cloudy'), (3, 'Confident Cloudy')]:
        count = np.sum(cloud_conf == val)
        pct = 100 * count / cloud_conf.size
        print(f"  {val} ({label}): {count} pixels ({pct:.1f}%)")
    print()
    
    print(f"Snow/Ice (Band 7): {np.sum(decoded['snow_ice'])} pixels ({100*np.mean(decoded['snow_ice']):.1f}%)")
    print(f"Shadow detected: {np.sum(decoded['shadow'])} pixels ({100*np.mean(decoded['shadow']):.1f}%)")
    print(f"Cirrus detected: {np.sum(decoded['cirrus'])} pixels ({100*np.mean(decoded['cirrus']):.1f}%)")
    print()
    
    # ========== COMPREHENSIVE DATA QUALITY FILTER ==========
    print("=" * 60)
    print("COMPREHENSIVE DATA QUALITY ASSESSMENT")
    print("=" * 60)
    
    # Multi-criteria filtering
    clear_sky = (cloud_conf <= 1)  # Confident/Probably Clear
    no_snow_b6 = (band6_snow == 0)
    no_snow_b7 = (~decoded['snow_ice'])
    high_quality = (band5_quality <= 1)
    night_only = (~decoded['is_day'])

    if np.sum(no_snow_b6) == 0:
        print("⚠️ Band 6 snow flag invalid or empty, ignoring snow filter.")
        no_snow_b6 = np.ones_like(no_snow_b6, dtype=bool)
    
    # Combined mask
    usable_mask = clear_sky & no_snow_b6 & no_snow_b7 & high_quality & night_only
    
    print("Filter Components:")
    print(f"  Clear sky (cloud conf 0-1): {np.sum(clear_sky)} ({100*np.mean(clear_sky):.1f}%)")
    print(f"  No snow (Band 6): {np.sum(no_snow_b6)} ({100*np.mean(no_snow_b6):.1f}%)")
    print(f"  No snow (Band 7): {np.sum(no_snow_b7)} ({100*np.mean(no_snow_b7):.1f}%)")
    print(f"  High quality (Flag 0-1): {np.sum(high_quality)} ({100*np.mean(high_quality):.1f}%)")
    print(f"  Nighttime only: {np.sum(night_only)} ({100*np.mean(night_only):.1f}%)")
    print()
    print(f"✓ FINAL USABLE PIXELS (all criteria): {np.sum(usable_mask)} ({100*np.mean(usable_mask):.1f}%)")
    print()
    
    # Filtered statistics
    ntl_filtered = band2_ntl_gapfilled[usable_mask]
    print("Gap-Filled NTL After Quality Filtering:")
    print(f"  Valid pixels: {len(ntl_filtered)}")
    print(f"  Mean intensity: {np.mean(ntl_filtered):.2f} nW·cm⁻²·sr⁻¹")
    print(f"  Median intensity: {np.median(ntl_filtered):.2f} nW·cm⁻²·sr⁻¹")
    print(f"  Std Dev: {np.std(ntl_filtered):.2f} nW·cm⁻²·sr⁻¹")
    print(f"  Max intensity: {np.max(ntl_filtered):.2f} nW·cm⁻²·sr⁻¹")
    print()
    
    # ========== VISUALIZATION ==========
    fig = plt.figure(figsize=(20, 12))
    
    # Row 1: Primary data bands
    ax1 = plt.subplot(3, 4, 1)
    im1 = ax1.imshow(band1_ntl_brdf, cmap='hot', 
                     vmin=np.nanpercentile(band1_ntl_brdf, 2), 
                     vmax=np.nanpercentile(band1_ntl_brdf, 98))
    ax1.set_title('Band 1: BRDF-Corrected NTL\n(Raw, with gaps)', fontweight='bold')
    ax1.axis('off')
    plt.colorbar(im1, ax=ax1, label='nW·cm⁻²·sr⁻¹', fraction=0.046)
    
    ax2 = plt.subplot(3, 4, 2)
    im2 = ax2.imshow(band2_ntl_gapfilled, cmap='hot', 
                     vmin=np.nanpercentile(band2_ntl_gapfilled, 2), 
                     vmax=np.nanpercentile(band2_ntl_gapfilled, 98))
    ax2.set_title('Band 2: Gap-Filled NTL ⭐\n(PRIMARY DATA)', fontweight='bold', color='red')
    ax2.axis('off')
    plt.colorbar(im2, ax=ax2, label='nW·cm⁻²·sr⁻¹', fraction=0.046)
    
    ax3 = plt.subplot(3, 4, 3)
    im3 = ax3.imshow(band3_lunar, cmap='Blues')
    ax3.set_title('Band 3: Lunar Irradiance', fontweight='bold')
    ax3.axis('off')
    plt.colorbar(im3, ax=ax3, label='Moon brightness', fraction=0.046)
    
    ax4 = plt.subplot(3, 4, 4)
    im4 = ax4.imshow(band4_latest_hq, cmap='viridis')
    ax4.set_title('Band 4: Latest HQ Retrieval', fontweight='bold')
    ax4.axis('off')
    plt.colorbar(im4, ax=ax4, label='Days since', fraction=0.046)
    
    # Row 2: Quality flags
    ax5 = plt.subplot(3, 4, 5)
    quality_display = band5_quality.copy().astype(float)
    quality_display[band5_quality == 255] = np.nan
    im5 = ax5.imshow(quality_display, cmap='RdYlGn_r', vmin=0, vmax=5)
    ax5.set_title('Band 5: Quality Flag ⭐\n(0-1=Good, 2+=Bad)', fontweight='bold')
    ax5.axis('off')
    cbar5 = plt.colorbar(im5, ax=ax5, fraction=0.046)
    cbar5.set_ticks([0, 1, 2, 3, 4, 5])
    cbar5.set_ticklabels(['HQ Pers', 'HQ Eph', 'Poor', 'Eclipse', 'Aurora', 'Glint'])
    
    ax6 = plt.subplot(3, 4, 6)
    ax6.imshow(band6_snow, cmap='Blues', vmin=0, vmax=1)
    ax6.set_title('Band 6: Snow Flag', fontweight='bold')
    ax6.axis('off')
    
    ax7 = plt.subplot(3, 4, 7)
    cloud_rgb = np.zeros((*cloud_conf.shape, 3))
    cloud_rgb[cloud_conf == 0] = [0, 1, 0]    # Green = clear
    cloud_rgb[cloud_conf == 1] = [0.5, 1, 0]  # Yellow = probably clear
    cloud_rgb[cloud_conf == 2] = [1, 0.5, 0]  # Orange = probably cloudy
    cloud_rgb[cloud_conf == 3] = [1, 0, 0]    # Red = cloudy
    ax7.imshow(cloud_rgb)
    ax7.set_title('Band 7: Cloud Confidence\n(Green=Clear, Red=Cloudy)', fontweight='bold')
    ax7.axis('off')
    
    ax8 = plt.subplot(3, 4, 8)
    landwater_colored = decoded['land_water'].astype(float)
    im8 = ax8.imshow(landwater_colored, cmap='terrain', vmin=0, vmax=5)
    ax8.set_title('Band 7: Land/Water Type', fontweight='bold')
    ax8.axis('off')
    plt.colorbar(im8, ax=ax8, label='Type', fraction=0.046)
    
    # Row 3: Composite masks and final product
    ax9 = plt.subplot(3, 4, 9)
    ax9.imshow(usable_mask, cmap='RdYlGn', vmin=0, vmax=1)
    ax9.set_title('Usable Data Mask\n(All Quality Filters)', fontweight='bold')
    ax9.axis('off')
    
    ax10 = plt.subplot(3, 4, 10)
    filtered_ntl = band2_ntl_gapfilled.copy()
    filtered_ntl[~usable_mask] = np.nan
    im10 = ax10.imshow(filtered_ntl, cmap='hot', 
                       vmin=np.nanpercentile(filtered_ntl, 2), 
                       vmax=np.nanpercentile(filtered_ntl, 98))
    ax10.set_title('FINAL: Quality-Filtered NTL\n(Ready for Analysis)', 
                   fontweight='bold', color='darkgreen')
    ax10.axis('off')
    plt.colorbar(im10, ax=ax10, label='nW·cm⁻²·sr⁻¹', fraction=0.046)
    
    # Histogram
    ax11 = plt.subplot(3, 4, 11)
    ax11.hist(ntl_filtered[ntl_filtered > 0], bins=50, color='orange', alpha=0.7, edgecolor='black')
    ax11.set_xlabel('Radiance (nW·cm⁻²·sr⁻¹)')
    ax11.set_ylabel('Frequency')
    ax11.set_title('Distribution of Filtered NTL', fontweight='bold')
    ax11.set_yscale('log')
    ax11.grid(alpha=0.3)
    
    # Summary statistics text
    ax12 = plt.subplot(3, 4, 12)
    ax12.axis('off')
    summary_text = f"""
    DATA QUALITY SUMMARY
    ═══════════════════════
    
    Total Pixels: {band2_ntl_gapfilled.size:,}
    Usable Pixels: {np.sum(usable_mask):,}
    Coverage: {100*np.mean(usable_mask):.1f}%
    
    FILTERED NTL STATISTICS:
    • Mean: {np.mean(ntl_filtered):.2f}
    • Median: {np.median(ntl_filtered):.2f}
    • Std: {np.std(ntl_filtered):.2f}
    • Max: {np.max(ntl_filtered):.2f}
    
    REJECTION REASONS:
    • Clouds: {100*np.mean(cloud_conf > 1):.1f}%
    • Snow: {100*np.mean(band6_snow == 1):.1f}%
    • Poor Quality: {100*np.mean(band5_quality > 1):.1f}%
    • Daytime: {100*np.mean(decoded['is_day']):.1f}%
    """
    ax12.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
              verticalalignment='center', bbox=dict(boxstyle='round', 
              facecolor='wheat', alpha=0.5))
    
    plt.suptitle(f'VIIRS VNP46A2 Complete Analysis: {tif_path.split("/")[-1]}', 
                 fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.show()
    
    print("=" * 60)
    print("Analysis complete! Ready for bird migration modeling.")
    print("=" * 60)