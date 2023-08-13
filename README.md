# solhycool_optimization
Source code of web app for the visualization of an optimization methodology applied to a combined cooling system for solar thermal processes within the Spanish national project SOLHYCOOL, from the Plataforma Solar de Almería - CIEMAT. 


## Create a new image

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


## Running the application locally

Set up the environment installing the dependencies from `requirerments.txt`

1. Set the required environment variables

```bash
    export CONF_FILE= "..."
```

2. Run the app

```bash
    gunicorn --env CONF_FILE=$CONF_FILE -b 0.0.0.0:8000 app:server
```