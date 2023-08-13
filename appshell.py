from collections import defaultdict

import dash_mantine_components as dmc
import dash
from dash import Output, Input, clientside_callback, html, dcc, page_container, State, callback
from dash_iconify import DashIconify

from pages import generate_nomenclature

""" Global variables"""


""" Functions and classes """
def create_home_link(label):
    # return dmc.Anchor(
    #     label,
    #     size="xl",
    #     href="/",
    #     underline=False,
    # )
    return dmc.Group([#dmc.Image(src='assets/libreSCADA_logo.png', fit='contain', width=40, height=40), 
                      dmc.ActionIcon(dmc.Image(src='assets/libreSCADA_logo.png', fit='contain', width=40, height=40)),
                      dmc.Anchor(label, size="xl", href="/optimization", underline=False, color=dmc.theme.DEFAULT_COLORS["red"][5])])


def create_main_nav_link(icon, label, href):
    return dmc.Anchor(
        dmc.Group(
            [
                DashIconify(
                    icon=icon, width=23, color=dmc.theme.DEFAULT_COLORS["indigo"][5]
                ),
                dmc.Text(label, size="sm"),
            ]
        ),
        href=href,
        variant="text",
        mb=5,
    )


navbar_icons = {
    "Data Display": "radix-icons:dashboard",
    "Inputs": "radix-icons:input",
    "Feedback": "radix-icons:info-circled",
    "Overlay": "radix-icons:stack",
    "Navigation": "radix-icons:hamburger-menu",
    "Typography": "radix-icons:letter-case-capitalize",
    "Layout": "radix-icons:container",
    "Miscellaneous": "radix-icons:mix",
    "Buttons": "radix-icons:button",
}


def create_header_link(icon, href, size=22, color="indigo"):
    return dmc.Anchor(
        dmc.ThemeIcon(
            DashIconify(
                icon=icon,
                width=size,
            ),
            variant="outline",
            radius=30,
            size=36,
            color=color,
        ),
        href=href,
        target="_blank",
    )


def create_header():
    return dmc.Header(
        height=70,
        fixed=True,
        px=25,
        children=[
            dmc.Stack(
                justify="center",
                style={"height": 70},
                children=dmc.Grid(
                    children=[
                        dmc.Col(
                            [
                                dmc.MediaQuery(
                                    create_home_link("SOLhycool | Plataforma Solar de Almería"),
                                    smallerThan="lg",
                                    styles={"display": "none"},
                                ),
                                dmc.MediaQuery(
                                    create_home_link("SOLhycool | PSA"),
                                    # largerThan="lg",
                                    # smallerThan="sm",
                                    query='(min-width: 1200px) or (max-width: 768px)',
                                    styles={"display": "none"},
                                ),
                                dmc.MediaQuery(
                                    create_home_link(label="SOLhycool"),
                                    largerThan='sm',
                                    styles={"display": "none"},
                                ),
                            ],
                            span="content",
                            pt=12,
                        ),
                        dmc.Col(
                            span="auto",
                            children=dmc.Group(
                                position="right",
                                spacing="xl",
                                children=[
                                    dmc.MediaQuery(
                                        [
                                            dmc.Group(
                                                position="center",
                                                spacing="xl",
                                                children=[
                                                    # About button
                                                    dmc.Button(
                                                        "About",
                                                        # variant="filled",
                                                        color="blue",
                                                        radius="sm",
                                                        size="md",
                                                        # compact=True,
                                                        loading=False,
                                                        id="button-about", 
                                                        n_clicks=0, 
                                                        variant="outline",
                                                        # gradient={"from": "teal", "to": "blue", "deg": 60}
                                                    ),
                                                    
                                                    # Nomenclature button
                                                    dmc.Tooltip(
                                                        multiline=True,
                                                        width=220,
                                                        withArrow=True,
                                                        transition="fade",
                                                        transitionDuration=200,
                                                        label="Click to show all system variables names with a description and a diagram",
                                                        children=[
                                                            dmc.Button(
                                                                "Nomenclature",
                                                                # variant="filled",
                                                                color="blue",
                                                                radius="sm",
                                                                size="md",
                                                                # compact=True,
                                                                loading=False,
                                                                id="header-nomenclature-button", 
                                                                n_clicks=0, 
                                                                variant="outline",
                                                                compact=False
                                                                # gradient={"from": "teal", "to": "blue", "deg": 60}
                                                            )
                                                        ],
                                                    ),
                                                    
                                                    # Login / logout button
                                                    # dmc.Tooltip(
                                                    #     withArrow=True,
                                                    #     transition="fade",
                                                    #     transitionDuration=200,
                                                    #     label="Click to login/logout",
                                                    #     children=[
                                                    #         dmc.Button(
                                                    #             "Login",
                                                    #             leftIcon=[DashIconify(icon="mdi:login-variant")],
                                                    #             id='navbar-login-button',
                                                    #             variant='subtle',
                                                    #             color='blue',
                                                    #             size='md'
                                                    #             )
                                                    #         ],
                                                    # ),
                                                    
                                                    # Light / Dark theme toggle
                                                    dmc.ActionIcon(
                                                        DashIconify(
                                                            icon="radix-icons:blending-mode", width=22
                                                        ),
                                                        variant="outline",
                                                        radius=30,
                                                        size=36,
                                                        color="yellow",
                                                        id="color-scheme-toggle",
                                                    ),

                                                    # Source code
                                                    create_header_link(
                                                        "radix-icons:github-logo",
                                                        "https://github.com/juan11iguel/combined-cooling-optimization",
                                                    ),
                                                    
                                                    # Portainer
                                                    create_header_link(
                                                        "bi:discord", "https://discord.gg/KuJkh4Pyq5"
                                                    ),
                                                ],
                                            ),
                                        ],
                                        smallerThan="md",
                                        styles={"display": "none"},
                                    ),
                                    
                                    
                                    
                                    
                                    # Hambuger menu
                                    dmc.MediaQuery(
                                        dmc.Menu(
                                            [
                                                dmc.MenuTarget(dmc.Burger(id="burger-button", opened=False)),
                                                dmc.MenuDropdown(
                                                    [
                                                        dmc.MenuItem(
                                                            "Login",
                                                            icon=DashIconify(icon="mdi:login-variant"),
                                                            id='navbar-login-button-burger',
                                                        ),
                                                        dmc.MenuDivider(),
                                                        dmc.MenuLabel("Utilities"),
                                                        dmc.MenuItem("About", id="button-about-burger"),
                                                        dmc.MenuItem("Nomenclature", id="header-nomenclature-button-2"),
                                                        dmc.MenuItem("Change color theme", id="color-scheme-toggle-burger"),                                                        
                                                        dmc.MenuDivider(),
                                                        dmc.MenuLabel("Links"),
                                                        dmc.MenuItem(
                                                            "Source Code",
                                                            href="https://github.com/Juasmis/librescada",
                                                            target="_blank",
                                                            icon=DashIconify(icon="radix-icons:github-logo"),
                                                        ),
                                                        dmc.MenuItem(
                                                            "Portainer",
                                                            href="https://github.com/Juasmis/librescada",
                                                            target="_blank",
                                                            icon=DashIconify(icon="radix-icons:github-logo"),
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            # width='target',
                                        ),
                                        
                                        # dmc.ActionIcon(
                                        #     DashIconify(
                                        #         icon="radix-icons:hamburger-menu",
                                        #         width=18,
                                        #     ),
                                        #     id="drawer-hamburger-button",
                                        #     variant="outline",
                                        #     size=36,
                                        # ),
                                        largerThan="md",
                                        styles={"display": "none"},
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            )
        ],
    )


def create_side_nav_content(nav_data):
    main_links = dmc.Stack(
        spacing="sm",
        mt=20,
        children=[
            create_main_nav_link(
                icon="material-symbols:rocket-launch-rounded",
                label="Getting Started",
                href="/getting-started",
            ),
            create_main_nav_link(
                icon="material-symbols:style",
                label="Styles API",
                href="/styles-api",
            ),
            create_main_nav_link(
                icon="material-symbols:measuring-tape-rounded",
                label="Style Props",
                href="/style-props",
            ),
            create_main_nav_link(
                icon="material-symbols:cookie-rounded",
                label="Dash Iconify",
                href="/dash-iconify",
            ),
        ],
    )
    # create component links
    sections = defaultdict(list)
    for entry in nav_data:
        if "section" in entry and entry["section"] not in [
            "Getting Started",
            "Styles API",
            "Style Props",
        ]:
            sections[entry["section"]].append((entry["name"], entry["path"]))

    links = []
    for section, items in sorted(sections.items()):
        links.append(
            dmc.Divider(
                labelPosition="left",
                label=[
                    DashIconify(
                        icon=navbar_icons[section], width=15, style={"marginRight": 10}
                    ),
                    section,
                ],
                my=20,
            )
        )
        links.extend(
            [
                dmc.NavLink(label=name, href=path, styles={"root": {"height": 32}})
                for name, path in items
            ]
        )

    return dmc.Stack(spacing=0, children=[main_links, *links, dmc.Space(h=20)], px=25)


def create_side_navbar(nav_data):
    return dmc.Navbar(
        fixed=True,
        id="components-navbar",
        position={"top": 70},
        width={"base": 300},
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                children=create_side_nav_content(nav_data),
            )
        ],
    )


def create_navbar_drawer(nav_data):
    return dmc.Drawer(
        id="components-navbar-drawer",
        overlayOpacity=0.55,
        overlayBlur=3,
        zIndex=9,
        size=300,
        children=[
            dmc.ScrollArea(
                offsetScrollbars=True,
                type="scroll",
                style={"height": "100vh"},
                pt=20,
                children=create_side_nav_content(nav_data),
            )
        ],
    )


def create_table_of_contents(toc_items):
    children = []
    for url, name, _ in toc_items:
        children.append(
            html.A(
                dmc.Text(name, color="dimmed", size="sm", variant="text"),
                style={"textTransform": "capitalize", "textDecoration": "none"},
                href=url,
            )
        )

    heading = dmc.Text("Table of Contents", mb=10, weight=500)
    toc = dmc.Stack([heading, *children], spacing=4, px=25, mt=20)

    return dmc.Aside(
        position={"top": 70, "right": 0},
        fixed=True,
        id="toc-navbar",
        width={"base": 300},
        zIndex=10,
        children=toc,
        withBorder=False,
    )


def create_appshell(config):
    return dmc.MantineProvider(
        dmc.MantineProvider(
            theme={
                "fontFamily": "'Inter', sans-serif",
                "primaryColor": "indigo",
                "components": {
                    "Button": {"styles": {"root": {"fontWeight": 400}}},
                    "Alert": {"styles": {"title": {"fontWeight": 500}}},
                    "AvatarGroup": {"styles": {"truncated": {"fontWeight": 500}}},
                },
            },
            inherit=True,
            children=[
                dcc.Store(id="theme-store", storage_type="local"),
                dcc.Location(id="url", refresh="callback-nav"),
                dmc.NotificationsProvider(
                    [
                        create_header(),
                        generate_nomenclature(config),
                        html.Div(
                            # id='appshell-content',
                            dmc.Tabs(
                                [
                                    # dmc.TabsList(
                                    #     # [dmc.Tab(f"Test page {i}", value=f"test_page_{i}") for i in range(1, 8)],
                                    #     [dmc.Tab(name, value=value) for name, value in zip(["Optimization", "Cooming soon"],
                                    #                                                        ["optimization", "cooming_soon"])],
                                    #     grow=True,
                                    # ),
                                ],
                                orientation='horizontal',
                                variant='outline',
                                value='optimization',
                                id='appshell-tabs',
                                pt=90,
                                px=10,
                                mx=20,
                            ),
                        ),
                        
                        
                        # create_side_navbar(nav_data),
                        # create_navbar_drawer(nav_data),
                        html.Div(
                            [
                                dmc.Container(size="lg", pt=10, children=page_container),
                            ],
                            id="wrapper",
                        ),
                    ]
                ),
            ],
        ),
        theme={"colorScheme": "light"},
        id="mantine-docs-theme-provider",
        withGlobalStyles=True,
        withNormalizeCSS=True,
    )


""" Callbacks """

# Light / Dark theme choice persistence
clientside_callback(
    """ function(data) { return data } """,
    Output("mantine-docs-theme-provider", "theme"),
    Input("theme-store", "data"),
)

# Light / Dark theme toggle
clientside_callback(
    """function(n_clicks, n_clicks_2, data) {
        if (data) {
            if (n_clicks || n_clicks_2) {
                const scheme = data["colorScheme"] == "dark" ? "light" : "dark"
                return { colorScheme: scheme } 
            }
            return dash_clientside.no_update
        } else {
            return { colorScheme: "light" }
        }
    }""",
    Output("theme-store", "data"),
    Input("color-scheme-toggle", "n_clicks"),
    Input("color-scheme-toggle-burger", "n_clicks"),
    State("theme-store", "data"),
)

# Don't know
# noinspection PyProtectedMember
# clientside_callback(
#     """
#     function(children) { 
#         window.scrollTo({ top: 0, behavior: 'smooth' });
#         return null
#     }
#     """,
#     Output("select-component", "value"),
#     Input("_pages_content", "children"),
# )


# Toggle hamburger menu
# clientside_callback(
#     """function(n_clicks) { return true }""",
#     Output("components-navbar-drawer", "opened"),
#     Input("drawer-hamburger-button", "n_clicks"),
#     prevent_initial_call=True,
# )     

# Toggle nomenclature
clientside_callback(
    """function(n1, n2) { return true }""",
    Output("nomenclature-modal", "opened"),
    Input("header-nomenclature-button", "n_clicks"),    
    Input("header-nomenclature-button-2", "n_clicks"),
    prevent_initial_call=True,
)

# @callback(
#     """function(n1, n2, openend) { return not_openend }""",
#     Output("nomenclature-modal", "opened"), 
#     Input("header-nomenclature-button", "n_clicks"),
#     Input("header-nomenclature-button-2", "n_clicks"),
#     State("nomenclature-modal", "opened"),
#     prevent_initial_call=True,
# )
# def toggle_nomenclature(n, n2 , opened):
#     ctx = dash.callback_context
#     if not ctx.triggered_id: return dash.no_update
    
#     return not opened

# Page selection with tabs
# @callback(
#     Output("url", "pathname"),
#     Input('appshell-tabs', 'value'),
#     prevent_initial_call=True,
# )
# def set_pathname(selected_tab):
#     if selected_tab:
#         return selected_tab
#     else: 
#         return dash.no_update
