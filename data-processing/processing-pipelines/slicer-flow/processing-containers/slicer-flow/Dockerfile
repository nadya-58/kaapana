FROM local-only/no-vnc-base:latest

LABEL IMAGE="slicer-flow"
LABEL VERSION="2022.10"
LABEL CI_IGNORE="False"

WORKDIR /src
# RUN mkdir -p /kaapana/mounted/slicer-data
# RUN mkdir -p /kaapana/mounted/workflows/data

# update required for libpulse-dev
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y libpulse-dev

# slicer-specific libraries
RUN apt-get install -y libglu1-mesa
RUN apt-get install -y libnss3
RUN apt-get install -y libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xkb1 libxkbcommon-x11-0
RUN apt-get install -y libxcb-shape0 libxcb-xinerama0 
RUN apt-get install -y libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-randr0 
# to clone slicer extensions
RUN apt-get install -y git

# Slicer 4.11.20200930 https://download.slicer.org/bitstream/60add70fae4540bf6a89bfb4
# Slicer 5.0.2 https://download.slicer.org/bitstream/6286ce04e8408647b39f803a
# Slicer 5.2.1 https://download.slicer.org/bitstream/637f7a7f517443dc5dc7326e
RUN SLICER_URL="https://download.slicer.org/bitstream/6286ce04e8408647b39f803a" && \
  curl -k -v -s -L $SLICER_URL | tar xz -C /tmp && \
  mv /tmp/Slicer* /opt/slicer

RUN chmod -R a+w /opt/slicer

#RUN useradd -m researcher -s /bin/bash && \
#    gpasswd -a researcher sudo && \
#    passwd -d researcher && passwd -u researcher && \
#    rm ~researcher/.bashrc ~researcher/.bash_logout ~researcher/.profile && \
#    sed -i -e '/^PS1/s/^/#/' /etc/bash.bashrc && \
#    sed -i -e '/stdout.*uname/s/^/#/' /etc/pam.d/login && \
#    echo 'source /etc/profile.d/prompt.sh' >> /etc/bash.bashrc


# install Slicer extension; extension name hardcoded in install-slicer-extension.py
COPY files/install-slicer-extension.py /opt/slicer
# see https://github.com/pieper/SlicerDockers/blob/master/slicer-plus/Dockerfile

# THIS CONFLICTS WITH user slicer not available at container build time
# temporarily disabled slicer extensions
# slicer extensions now enabled via startSlicer.sh
#RUN apt-get install -y xvfb
#RUN su slicer -c "xvfb-run --auto-servernum \
#    /opt/slicer/Slicer --python-script /opt/slicer/install-slicer-extension.py --no-splash --no-main-window"

# download an additional slicer extension
# installation into slicer happens after container starts
WORKDIR /opt/slicer
RUN git clone -b multiple_server https://github.com/deepakri201/mpReview.git

# install wrapper script for reading Kaapana data via DAG flow and tasklist.json
COPY files/SlicerFlow.py /opt/slicer

#?? from SlicerDockers/blob/master/x11/Dockerfile
RUN echo "allowed_users=anybody" > /etc/X11/Xwrapper.config

RUN mkdir -p /home/slicer/Desktop
COPY files/startSlicer.sh /home/slicer/Desktop/
RUN chmod +x /home/slicer/Desktop/startSlicer.sh

# RUN ln -s /data /home/slicer/Desktop/
# WORKDIR /data

# A supervisord config is used to make the application managed
COPY files/supervisord.conf /etc/supervisor/conf.d/
