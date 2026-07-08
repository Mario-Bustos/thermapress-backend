from base64 import b64encode
from pathlib import Path


def _load_logo_data_uri() -> str | None:
    path = Path(__file__).resolve().parent / "images" / "logo-no-bg.png"
    if not path.exists():
        return None

    encoded = b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"


LOGO_DATA_URI = _load_logo_data_uri()


def build_email(user_email: str, articles: list[dict]) -> str:
    if not articles:
        articles_html = """
        <tr>
          <td style="padding: 40px; text-align: center; color: #c9c9c9;">
            No articles found for your selected topics today. Try adding more sources or topics in your account settings.
          </td>
        </tr>
        """
    else:
        articles_html = ''.join([_article_card(a, i) for i, a in enumerate(articles)])

    logo_html = ""
    if LOGO_DATA_URI is not None:
        logo_html = f"""
          <tr>
            <td style="padding: 24px 40px 0; display: flex; align-items: center;">
              <img src=\"{LOGO_DATA_URI}\" alt=\"ThermaPress logo\" width=\"120\" style=\"display:block; max-width:100%; height:auto;\" />
            </td>
          </tr>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
      <title>Your ThermaPress Newsletter</title>
    </head>
    <body style="margin:0; padding:0; background:#0f0a1e; font-family:'Helvetica Neue', Arial, sans-serif;">

      <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f0a1e; padding: 32px 0;">
        <tr>
          <td align="center">
            <table width="620" cellpadding="0" cellspacing="0" style="max-width:620px; width:100%;">

              <!-- Header -->
              <tr>
                <td style="background: linear-gradient(90deg, #311a52 0%, #563e7c 100%); border-radius: 16px 16px 0 0; padding: 24px 40px;">
                  {logo_html}
                  <h1 style="margin:0; font-size:28px; font-weight:800; color:#ffffff; letter-spacing:-0.5px;">
                    <span style="color:#ff7a2f;">Therma</span>Press
                  </h1>
                  <p style="margin:8px 0 0; font-size:14px; color:#c9c9c9;">
                    Your personalized newsletter — curated just for you.
                  </p>
                </td>
              </tr>

              <!-- Articles -->
              <tr>
                <td style="background:#1d1035; padding: 0 40px 32px;">
                  <table width="100%" cellpadding="0" cellspacing="0">
                    {articles_html}
                  </table>
                </td>
              </tr>

              <!-- Footer -->
              <tr>
                <td style="background:#170c27; border-radius: 0 0 16px 16px; padding: 24px 40px; text-align:center;">
                  <p style="margin:0; font-size:12px; color:#563e7c;">
                    You're receiving this because you signed up for ThermaPress.
                    <br/>
                    Manage your preferences at
                    <a href="https://yourdomain.com/account" style="color:#ff7a2f; text-decoration:none;">your account settings</a>.
                  </p>
                </td>
              </tr>

            </table>
          </td>
        </tr>
      </table>

    </body>
    </html>
    """


def _article_card(article: dict, index: int) -> str:
    border_top = 'border-top: 1px solid #2a1547;' if index > 0 else ''
    return f"""
    <tr>
      <td style="padding: 24px 0; {border_top}">
        <p style="margin: 0 0 6px; font-size: 11px; font-weight: 700; color: #ff7a2f;
                  text-transform: uppercase; letter-spacing: 0.08em;">
          {article['source']}
        </p>
        <a href="{article['link']}" style="text-decoration:none;">
          <h2 style="margin: 0 0 10px; font-size: 17px; font-weight: 700;
                     color: #ffffff; line-height: 1.4;">
            {article['title']}
          </h2>
        </a>
        <p style="margin: 0 0 12px; font-size: 14px; color: #c9c9c9; line-height: 1.6;">
          {article['summary']}
        </p>
        <a href="{article['link']}"
           style="display:inline-block; padding: 8px 18px; border-radius: 8px;
                  background: linear-gradient(90deg, #311a52 0%, #563e7c 100%);
                  color: #ffffff; font-size: 13px; font-weight: 600;
                  text-decoration: none;">
          Read more →
        </a>
      </td>
    </tr>
    """