$provision_root = <<'SCRIPT_ROOT'
apt-get update
apt-get upgrade -y
apt-get install -y build-essential docker.io git jq libltdl-dev python3-pip whois
apt-get autoremove -y
usermod -aG docker vagrant
SCRIPT_ROOT

$provision_user = <<'SCRIPT_USER'
mkdir -p ${HOME}/local
mkdir -p ${HOME}/golang/src
ln -s /vagrant/network ${HOME}/golang/src
cd
wget --quiet https://redirector.gvt1.com/edgedl/go/go1.10.3.linux-amd64.tar.gz
tar -xf go1.10.3.linux-amd64.tar.gz
mv go ${HOME}/local/

mkdir -p ~/.vim/autoload ~/.vim/bundle
curl -LSso ~/.vim/autoload/pathogen.vim https://tpo.pe/pathogen.vim
git clone https://github.com/fatih/vim-go.git ~/.vim/bundle/vim-go


pip3 install --user ansible
pip3 install --user docker-compose
pip3 install --user softlayer


cat <<'EOF_BASHRC' > $HOME/.bashrc
export GOROOT=${HOME}/local/go
export GOPATH=${HOME}/golang
export PATH=${GOROOT}/bin:${HOME}/local/bin:${HOME}/.local/bin:${PATH}


cd /vagrant

EOF_BASHRC

SCRIPT_USER

Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/bionic64"
    config.vm.provision :shell, inline: $provision_root
    config.vm.provision :shell, privileged: false, inline: $provision_user
    config.vm.provider "virtualbox" do |vb|
        vb.customize ["modifyvm", :id, "--name", "fabric"]
        vb.customize ["modifyvm", :id, "--cpus", "2"]
        vb.customize ["modifyvm", :id, "--cpuexecutioncap", "90"]
        vb.customize ["modifyvm", :id, "--memory", "4096"]
    end
    config.vm.hostname = "fabric"

    if File.exists?(File.expand_path("~/.gitconfig"))
        config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
    end

    if File.exists?(File.expand_path("~/.vimrc"))
        config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
    end
end
