import os
from folium_screanshot.screanshot import AirialImageRenderBySelenium
from folium_screanshot import map_generator


if __name__ == '__main__':
    base_point_lat, base_point_lon = [34.841023, 137.3243984]
    base_point_direction_degree = 20
    rel_dist_depth_metre = 40
    rel_dist_width_metre = 20
    rel_dist_height_metre = 10

    selenium_server_adress: str = "http://localhost:4444/wd/hub"
    share_dir_path_in_this_server: str = "."
    share_dir_abspath_in_selenium_server: str = "/share"

    image_name = "sample.png"
    image_path = os.path.join("images", image_name)

    folium_map = map_generator.create_map_display_relative_position_at_two_points(
        base_point_lat=base_point_lat,
        base_point_lon=base_point_lon,
        base_point_direction_degree=base_point_direction_degree,
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
