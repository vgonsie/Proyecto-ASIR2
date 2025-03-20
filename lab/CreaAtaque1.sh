virt-install --name ataque1 \
--ram 2048 --vcpus 2 \
--disk path=/var/lib/libvirt/images/ataque1.qcow2,size=10 \
--os-type linux --os-variant ubuntu22.04 \
--network bridge=virbr0 \
--cdrom /var/lib/libvirt/boot/ubuntu.iso \
--graphics none --console pty,target_type=serial
