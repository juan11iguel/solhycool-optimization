# solhycool_optimization
Source code of web app for the visualization of an optimization methodology applied to a combined cooling system for solar thermal processes within the Spanish national project SOLHYCOOL, from the Plataforma Solar de Almería - CIEMAT. 

## Deployment

1. In the server, create three new folders:
- `docker_compose_files`, where the compose files for the deployment of the app, traefik, portainer, etc will be loaded. Templates are available in the [docker_compose_files](docker_compose_files) directory.
- `configuration_files`, where the `hjson` file with the app configuration is stored. A template is avaialable at [wascop_app.hjson](configuration_files)
- `assets/wascop_app`, here the necessary assets to lauch the app are stored: diagrams, logo images, result files, css stylesheets, etc.

2. Launch the base services:
```bash
docker compose -f docker_compose_files/portainer.yml --project-name base up -d
```
```bash
docker compose -f docker_compose_files/traefik.yml --project-name base up -d
```
```bash
docker compose -f docker_compose_files/watchtower.yml --project-name base up -d
```
3. Run the web app and the dynamic results updater to make new results available (pareto front and diagrams) as soon as new data is copied to the assets folder.

## Features

- Continous integration. New docker images are built automatically at every tagged push.
- Continuous deployment. By using watchtower, every time a new image is pushed to the repository registry, the deployment at PSA is updated (i.e. broken most likely).
- When new results are made available, new diagrams are generated and the results dicitionary is updated with the new data making it available at runtime in the app.
- Cached outputs via a redis server.

## Pending

- In mobile version, header should not be permanent (takes too much space in lanscape mode)
- In mobile version, remove icons from evaluate and export buttons.
- When pareto optimization is not available, just show the cloud of points and display the identified minimums.
- Generate a pdf report when some operation conditions are selected.
- When a point is selected, generate some plots to evaluate the contributors to the electrical consumption, and compare the operation point with some extremes (only DC or only WCT).
- In mobile version, remove padding and margins from paper components to better take advantage of the available space.
- Add telemetry just to gather some basic anonymous information (number of visitors, etc)

## How to

### Create a new image

In order to trigger an image build:

1. Create a new tag (must be preceded by a v):
```
 git tag v1.0.X
```

2. Push the tag:
```
 git push --tags
```

3. Push the new commit that will trigger the build
```
 git push
```


### Running the application locally

Set up the environment installing the dependencies from `requirerments.txt`

1. Set the required environment variables

```bash
    export CONF_FILE= "..."
```
2. Run the app

```bash
    gunicorn --env CONF_FILE=$CONF_FILE -b 0.0.0.0:8000 app:server
```

## Warning

This is a work in progress made public for a particular implementation of the results visualization of an optimization strategy. At the current conditions it is not expected to be used by any users, but the source code is freely available to check and a running implementation is avaialable at [external.psa.es/solhycool/optimization](https://external.psa.es/solhycool/optimization).

### Acknowledgments
