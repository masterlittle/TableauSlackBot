
def get_image_view(image_name:str, url):
    return [
        {
            "type": "image",
            "title": {
                "type": "plain_text",
                "text": image_name
            },
            "block_id": "image4",
            "image_url": url,
            "alt_text": "An incredibly cute kitten."
        },
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": ":level_slider:  Queuing up your Daily Dose of Data  :control_knobs:"
        }
    },
    {
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "Want to see more? <https://www.tableau.com/ Insert Your Link to All Dashboards Here>"
            }
        ]
    }
]