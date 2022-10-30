import os
from folium_screanshot.screanshot import AirialImageRenderBySelenium
import folium_map_generator


if __name__ == '__main__':
    base_point_lat, base_point_lon = [34.8412, 137.3246] #[34.841023, 137.3243984]
    base_point_direction_degree = 20
    move_point_lat, move_point_lon = [34.841023, 137.3243984] #[34.8412, 137.3248]
    rel_dist_depth_metre = 40
    rel_dist_width_metre = 20
    rel_dist_height_metre = 10

    selenium_server_adress: str = "http://localhost:4444/wd/hub"
    share_dir_path_in_this_server: str = "."
    share_dir_abspath_in_selenium_server: str = "/share"

    image_name = "sample.png"
    image_path = os.path.join("images", image_name)

    folium_map = folium_map_generator.create_map_display_base_point_moving(
        base_point_lat=base_point_lat,
        base_point_lon=base_point_lon,
        base_point_direction_degree=base_point_direction_degree,
        moved_point_lat=move_point_lat,
        moved_point_lon=move_point_lon,
        rel_dist_depth_metre=rel_dist_depth_metre,
        rel_dist_width_metre=rel_dist_width_metre,
        rel_dist_height_metre=rel_dist_height_metre,
    )
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
