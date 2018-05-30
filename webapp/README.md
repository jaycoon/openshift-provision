# OpenShift Provision

## Notes

```bash
podman build --tag pipenv-python3 --file Dockerfile.pipenv .
podman build --tag openshift-provision --file Dockerfile .

podman run -it --rm --name openshift-provision --user $(id -u $USER) --volume $(pwd):/app:z --publish 8000:8000 openshift-provision python manage.py [COMMAND]
podman run -it --rm --name openshift-provision --user $(id -u $USER) --volume $(pwd):/app:z --publish 8000:8000 openshift-provision
```

