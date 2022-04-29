HTML = """
            <!-- HTML for static distribution bundle build -->
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <title>Swagger UI</title>
                    <link rel="stylesheet" type="text/css"
                    href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui.css" >
                    <style>
                    html
                    {{
                        box-sizing: border-box;
                        overflow: -moz-scrollbars-vertical;
                        overflow-y: scroll;
                    }}

                    *,
                    *:before,
                    *:after
                    {{
                        box-sizing: inherit;
                    }}

                    body
                    {{
                        margin:0;
                        background: #fafafa;
                    }}
                    </style>
                </head>

                <body>
                    <div id="swagger-ui"></div>

                    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js"></script>
                    <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-standalone-preset.js"></script>
                    <script>
                    window.onload = function() {{
                    var full = location.protocol + '//' + location.hostname + (location.port ? ':' + location.port : '');
                    // Begin Swagger UI call region
                    const ui = SwaggerUIBundle({{
                        url: "{spec_url}",
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                        SwaggerUIBundle.presets.apis,
                        SwaggerUIStandalonePreset
                        ],
                        plugins: [
                        SwaggerUIBundle.plugins.DownloadUrl
                        ],
                        oauth2RedirectUrl: full + "/{spec_path}/swagger/oauth2-redirect.html",
                        layout: "StandaloneLayout"
                    }})
                    ui.initOAuth({{
                        clientId: "{client_id}",
                        clientSecret: "{client_secret}",
                        realm: "{realm}",
                        appName: "{app_name}",
                        scopeSeparator: "{scope_separator}",
                        additionalQueryStringParams: {additional_query_string_params},
                        useBasicAuthenticationWithAccessCodeGrant: {use_basic_authentication_with_access_code_grant},
                        usePkceWithAuthorizationCodeGrant: {use_pkce_with_authorization_code_grant}
                    }})
                    // End Swagger UI call region

                    window.ui = ui
                    }}
                </script>
                </body>
            </html>"""
