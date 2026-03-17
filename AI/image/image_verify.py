import downloader
import metadata
import c2pa
import watermark 
import visual_artifacts
import frequency_domain_analysis
import pixel_level_analysis
import sensor_pattern_noise
import compression_artifact_analysis
import gan
import perturbation_robustness_testing
import decision_engine


def verify(image_url):
    try:
        img = downloader.process(image_url)
        image_bytes = img["bytes"]
        pil_image = img["pil_image"]
        gray_pixels = img["pixels_gray"]

        img_metadata = metadata.process(image_bytes)
        img_c2pa = c2pa.process(image_bytes)
        img_watermark = watermark.process(image_bytes)
        img_visual_artifacts = visual_artifacts.process(pil_image)
        img_frequency_domain_analysis = frequency_domain_analysis.process(image_bytes)
        img_pixel_level_analysis = pixel_level_analysis.process(image_bytes)
        img_sensor_pattern_noise = sensor_pattern_noise.process(gray_pixels)
        img_compression_artifact_analysis = compression_artifact_analysis.process(image_bytes)
        img_gan = gan.process(image_bytes)
        img_perturbation_robustness_testing = perturbation_robustness_testing.process(image_bytes)
        

        data = {
            "metadata": img_metadata,
            "c2pa": img_c2pa,
            "watermark": img_watermark,
            "visual": img_visual_artifacts,
            "frequency_domain_analysis": img_frequency_domain_analysis,
            "pixel": img_pixel_level_analysis,
            "sensor_pattern_noise": img_sensor_pattern_noise,
            "compression_artifact_analysis": img_compression_artifact_analysis,
            "gan": img_gan,
            "perturbation": img_perturbation_robustness_testing
        }
        
        img_decision_engine = decision_engine.process(data) 
        
        # print("Metadata: ", img_metadata)
        # print("c2pa: ", img_c2pa)
        # print("Watermark: ", img_watermark)
        # print("Visual Artifacts: ", img_visual_artifacts)
        # print("Frequency Domain Analysis: ", img_frequency_domain_analysis)
        # print("Pixel Level Analysis: ", img_pixel_level_analysis)
        # print("Sensor Pattern Noise: ", img_sensor_pattern_noise)
        # print("Compression Artifact Analysis: ", img_compression_artifact_analysis)
        # print("Gan: ", img_gan)
        # print("Perturbation Robustness Testing: ", img_perturbation_robustness_testing)
        # print("Decision Engine: ", img_decision_engine)

        return img_decision_engine
    except Exception as e:
        print(e)


# image_url_1 = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
# image_url_2 = "https://res.cloudinary.com/dfamljkyo/image/upload/v1766424802/jqb9jtdecfetvkzgegqz.png"
# print(verify(image_url_2))