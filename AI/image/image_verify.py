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
import concurrent.futures


def verify(image_url):
    try:
        img = downloader.process(image_url)
        image_bytes = img["bytes"]
        pil_image = img["pil_image"]
        gray_pixels = img["pixels_gray"]

        with concurrent.futures.ThreadPoolExecutor() as executor:
            f_metadata = executor.submit(metadata.process, image_bytes)
            f_c2pa = executor.submit(c2pa.process, image_bytes)
            f_watermark = executor.submit(watermark.process, image_bytes)
            f_visual = executor.submit(visual_artifacts.process, pil_image)
            f_frequency = executor.submit(frequency_domain_analysis.process, image_bytes)
            f_pixel = executor.submit(pixel_level_analysis.process, image_bytes)
            f_sensor = executor.submit(sensor_pattern_noise.process, gray_pixels)
            f_compression = executor.submit(compression_artifact_analysis.process, image_bytes)
            f_gan = executor.submit(gan.process, image_bytes)
            f_perturbation = executor.submit(perturbation_robustness_testing.process, image_bytes)

            data = {
                "metadata": f_metadata.result(),
                "c2pa": f_c2pa.result(),
                "watermark": f_watermark.result(),
                "visual": f_visual.result(),
                "frequency_domain_analysis": f_frequency.result(),
                "pixel": f_pixel.result(),
                "sensor_pattern_noise": f_sensor.result(),
                "compression_artifact_analysis": f_compression.result(),
                "gan": f_gan.result(),
                "perturbation": f_perturbation.result()
            }
        
        img_decision_engine = decision_engine.process(data) 
        
        return img_decision_engine
    except Exception as e:
        print(e)


# image_url_1 = "https://upload.wikimedia.org/wikipedia/commons/4/47/PNG_transparency_demonstration_1.png"
# image_url_2 = "https://res.cloudinary.com/dfamljkyo/image/upload/v1766424802/jqb9jtdecfetvkzgegqz.png"
# print(verify(image_url_2))