import os
from folium_screanshot.screanshot import AirialImageRenderBySelenium
from folium_screanshot.map_generator import create_map_with_relative_distance_from_camera


if __name__ == '__main__':
    c_lat, c_lon = [34.841023, 137.3243984]
    d_metre = 20
    d_degree = 45
    w_metre = 40
    h_metre = 18.333333333

    selenium_server_adress: str = "http://localhost:4444/wd/hub"
    share_dir_path_in_this_server: str = "."
    share_dir_abspath_in_selenium_server: str = "/share"

    image_name = "sample.png"
    image_path = os.path.join("images", image_name)

    folium_map = create_map_with_relative_distance_from_camera(
        c_lat=c_lat,
        c_lon=c_lon,
        d_degree=d_degree,
        d_metre=d_metre,
        w_metre=w_metre,
        h_metre=h_metre,
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
