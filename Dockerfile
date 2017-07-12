RUN sudo docker pull docker.haltu.net/haltu/env/heliconia:salt_config
RUN sudo docker tag docker.haltu.net/haltu/env/heliconia:salt_config heliconia

FROM heliconia

RUN sudo pip3 install -r requirements.txt