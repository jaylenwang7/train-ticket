# Train Ticket: A New Version

## To build

1. Set up docker credentials by setting set-docker.sh:

  ```
  #!/bin/bash

  # Set Docker Hub credentials as environment variables
  export DOCKER_HUB_USERNAME="USERNAME"
  export DOCKER_HUB_PASSWORD="PASSWORD"
    
  ```

2. Run the following commands:

  ```
  chmod +x set-docker.sh
  sudo ./set-docker.sh
  sudo ./setup-build.sh
  ```

3. To build the project, run the following command:

  ```
  sudo ./build.sh
  ```

  OR

  ```
  sudo ./build_some.sh DIRS.txt
  ```
    
  where DIRS.txt is a file containing the directories to build, e.g.,
  
  ```
  ts-auth-service
  ts-config-service
  ts-discovery-service
  ...
  ```

4. (Optional) If you want to redeploy a kubernetes deployment using the new image, run the following command:

  ```
  sudo kubectl rollout restart deployment <DEPLOYMENT_NAME> -n ts
  ```