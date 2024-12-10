import io
from typing import Optional

import PyPDF2

# load logging
from utils.ml_logging import get_logger

logger = get_logger()


def extract_html_from_page(page_contents: dict) -> Optional[dict]:
    """
    Extracts HTML from the page

    :param page_contents: Dictionary with all metadta fields.
    :return: Extracted HTML from the page as a string, or None if extraction fails.
    """
    try:
        return _find_elements(page_contents)
        # return _construct_html_document(elements)

    except Exception as e:
        logger.error(f"An unexpected error occurred during PDF text extraction: {e}")

    return None

def _parse_image_url(url: str) -> dict:
    #Example: /sites/test/SiteAssets/SitePages/My-page-title/2800131800-camping_big_2.jpeg
    parts = url.split('/')
    if 'sites' not in parts:
        return {"image_url": url}
    site_index = parts.index('sites') + 1
    site_name = parts[site_index]   
    site_url = '/'.join(parts[:site_index+1])

    drive_index = site_index+1
    drive_name = parts[drive_index]

    asset_path = '/'.join(parts[drive_index + 1:])
    return {'site_name': site_name, 'site_url': site_url, 'drive_name' : drive_name, 'asset_path': asset_path, "image_url": url}


def _construct_html_document(elements: list) -> str:
    html_content = "<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n<title>Document</title>\n</head>\n<body>\n"
    concatenated_elements = ''.join(elements)
    html_content += f"<div>{concatenated_elements}</div>\n"
    html_content += "</body>\n</html>"
    return html_content

def _find_elements(data, result=None):
    if result is None:
        result = {'contents': [], 'images':[]}

    if isinstance(data, dict):
        for key, value in data.items():
            if key == 'innerHtml':
              result['contents'].append(value)
            elif key == 'imageSources' and isinstance(value, list):
                for image in value:
                    if 'value' in image and image['value'] != None:
                        img_src = image['value']
                        result['contents'].append(f'<img src=\"{img_src}\" />')
                        result['images'].append(_parse_image_url(img_src))
            else:
                _find_elements(value, result)
    elif isinstance(data, list):
        for item in data:
            _find_elements(item, result)

    return result