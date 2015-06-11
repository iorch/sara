# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "debian/jessie64"
  config.vm.box_url = "https://atlas.hashicorp.com/debian/boxes/jessie64"

  config.vm.provider "virtualbox" do |v|
    v.memory = 1536
    #v.cpus = 2
  end

  config.vm.network :forwarded_port, guest: 5000, host: 5000
  config.vm.network :private_network, ip: "192.168.33.10"

  config.vm.provision "ansible" do |ansible|
    ansible.playbook = "provisioning/playbook.yml"
    ansible.inventory_path = "provisioning/vagrant_ansible_inventory"
    ansible.verbose = "v"
  end

end
