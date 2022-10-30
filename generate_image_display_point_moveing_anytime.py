import os
from folium_screanshot.screanshot import AirialImageRenderBySelenium
import folium_map_generator


if __name__ == '__main__':
    coords = [
        [34.8412, 137.3246],
        [34.841023, 137.3243984],
        [34.8411, 137.3245],
    ]
    image_name = "display_point_moving_anytime.png"

    selenium_server_adress: str = "http://localhost:4444/wd/hub"
    share_dir_path_in_this_server: str = "."
    share_dir_abspath_in_selenium_server: str = "/share"

    image_path = os.path.join("images", image_name)

    folium_map = folium_map_generator.create_map_display_point_moving_anytime(coords)
    airial_image_generator = AirialImageRenderBySelenium(
        selenium_server_adress=selenium_server_adress,
        share_dir_path_in_this_server=share_dir_path_in_this_server,
        share_dir_abspath_in_selenium_server=share_dir_abspath_in_selenium_server,
    )
    image_pil = airial_image_generator.render(
        folium_map=folium_map,
    )
    if image_pil is not None:
        print("save image.")
        image_pil.save(image_path)
