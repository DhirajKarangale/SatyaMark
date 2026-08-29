import numpy as np

def extract_feature_vector(data: dict) -> list[float]:
    """Flattens the deeply nested heuristic dictionary into a 1D feature vector."""
    features = []

    # 1. Metadata
    meta = data.get("metadata", {}).get("analysis", {})
    features.append(1.0 if meta.get("has_exif") else 0.0)
    features.append(1.0 if meta.get("camera_valid") else 0.0)
    features.append(1.0 if meta.get("suspicious") else 0.0)

    # 2. C2PA
    c2pa = data.get("c2pa", {})
    features.append(1.0 if c2pa.get("c2pa_present") else 0.0)
    features.append(1.0 if c2pa.get("valid_signature") else 0.0)

    # 3. Sensor Pattern Noise
    spn = data.get("sensor_pattern_noise", {}).get("spn_metrics", {})
    features.append(float(spn.get("horizontal_correlation", 0.0)))
    features.append(float(spn.get("vertical_correlation", 0.0)))

    # 4. GAN & Diffusion
    gan = data.get("gan", {})
    gan_checker = gan.get("gan_checkerboard_artifacts", {})
    diff_samp = gan.get("diffusion_sampling_artifacts", {})
    features.append(float(gan_checker.get("mean_checker_peaks", 0.0)))
    features.append(float(diff_samp.get("radial_peak_density", 0.0)))

    # 5. Physics & Geometry
    physics = data.get("physics_geometry", {}).get("physics_and_geometry", {})
    illum = physics.get("illumination", {})
    features.append(float(illum.get("lighting_consistency_score", 0.0)))
    features.append(float(illum.get("lighting_angle_variance", 0.0)))

    # 6. ELA
    ela = data.get("ela_analysis", {})
    features.append(1.0 if ela.get("is_suspicious") else 0.0)

    # 7. Autoencoder
    ae = data.get("autoencoder_reconstruction", {})
    features.append(1.0 if ae.get("is_suspiciously_simple") else 0.0)

    # 8. Diffusion Latent
    latent = data.get("diffusion_latent_analysis", {})
    features.append(1.0 if latent.get("is_diffusion_aligned") else 0.0)
    features.append(float(latent.get("latent_kurtosis", 0.0)))

    # 9. Benfords Law
    benford = data.get("benfords_law", {})
    features.append(float(benford.get("benford_chi_square", 1.0)))

    # 10. Chromatic Aberration
    ca = data.get("chromatic_aberration", {})
    features.append(1.0 if ca.get("has_natural_lens_dispersion") else 0.0)
    features.append(float(ca.get("aberration_shift", 1.0)))

    # 11. Patch Analysis
    patch = data.get("patch_analysis", {})
    features.append(1.0 if patch.get("is_suspicious") else 0.0)

    # 12. Copy Move
    copy_move = data.get("copy_move", {})
    features.append(1.0 if copy_move.get("is_copy_move_detected") else 0.0)
    features.append(float(copy_move.get("patch_matches_found", 0.0)))

    # 13. Frequency
    freq = data.get("frequency_domain_analysis", {}).get("frequency_analysis", {})
    features.append(float(freq.get("spectral_flatness", 0.0)))

    # 14. Perturbation
    pert = data.get("perturbation", {}).get("perturbation_robustness", {})
    features.append(float(pert.get("std_similarity", 0.0)))

    # 15. Watermark
    wm = data.get("watermark", {}).get("watermark_analysis", {})
    features.append(1.0 if wm.get("watermark_detected") else 0.0)
    features.append(float(wm.get("watermark_score", 0.0)))

    # 16. Visual Artifacts
    vis = data.get("visual", {}).get("visual_artifact_features", {})
    noise = vis.get("noise", {})
    sym = vis.get("symmetry", {})
    tex = vis.get("texture_blocks", {})
    features.append(float(noise.get("residual_variance", 0.0)))
    features.append(float(sym.get("symmetry_score", 0.0)))
    features.append(float(tex.get("block_variance_global", 0.0)))

    # 17. Compression Analysis
    comp = data.get("compression_artifact_analysis", {}).get("compression_analysis", {})
    features.append(float(comp.get("double_jpeg_probability", 0.0)))
    features.append(float(comp.get("dct_zero_ratio", 0.0)))

    # 18. Pixel Level
    pixel = data.get("pixel", {})
    kurt = pixel.get("kurtosis", {})
    r_k = kurt.get("r", 0.0)
    g_k = kurt.get("g", 0.0)
    b_k = kurt.get("b", 0.0)
    avg_k = (r_k + g_k + b_k) / 3.0 if (r_k and g_k and b_k) else 0.0
    features.append(avg_k)

    neighbor = pixel.get("neighbor_correlation", {})
    features.append(float(neighbor.get("horizontal", 0.0)))
    features.append(float(neighbor.get("vertical", 0.0)))

    res_noise = pixel.get("residual_noise", {})
    features.append(float(res_noise.get("kurtosis", 0.0)))

    # Normalize NaNs/Infs
    features = np.nan_to_num(features, nan=0.0, posinf=1.0, neginf=-1.0).tolist()
    return features
