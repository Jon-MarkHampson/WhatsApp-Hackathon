import cairosvg
import os

def create_favicons():
    # Ensure static directory exists
    if not os.path.exists('static'):
        os.makedirs('static')

    # Convert SVG to different PNG sizes
    sizes = [16, 32, 180]
    for size in sizes:
        cairosvg.svg2png(
            url='static/mm_light.svg',
            write_to=f'static/favicon-{size}x{size}.png',
            output_width=size,
            output_height=size
        )

    # Create site.webmanifest
    manifest_content = '''{
    "name": "Meme Machine",
    "short_name": "Meme Machine",
    "icons": [
        {
            "src": "/static/android-chrome-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "/static/android-chrome-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ],
    "theme_color": "#ffffff",
    "background_color": "#ffffff",
    "display": "standalone"
}'''

    with open('static/site.webmanifest', 'w') as f:
        f.write(manifest_content)

if __name__ == '__main__':
    create_favicons() 