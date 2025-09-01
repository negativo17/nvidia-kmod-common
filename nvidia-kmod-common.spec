%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d

# gsp_*.bin: ELF 64-bit LSB executable, UCB RISC-V
%global _binaries_in_noarch_packages_terminate_build 0
%global __brp_strip %{nil}

Name:           nvidia-kmod-common
Version:        580.82.07
Release:        1%{?dist}
Summary:        Common file for NVIDIA's proprietary driver kernel modules
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html

BuildArch:      noarch

Source0:        %{name}-%{version}.tar.xz
Source17:       nvidia-boot-update
Source18:       kernel.conf
Source19:       nvidia-modeset.conf
Source20:       nvidia.conf
Source21:       60-nvidia.rules
Source24:       99-nvidia.conf

# UDev rule location (_udevrulesdir) and systemd macros:
BuildRequires:  systemd-rpm-macros

Requires:       nvidia-modprobe
Requires:       nvidia-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Obsoletes:      cuda-nvidia-kmod-common < %{?epoch:%{epoch}:}%{version}

%description
This package provides the common files required by all NVIDIA kernel module
package variants.
 
%prep
%autosetup

%install
# Script for post/preun tasks
install -p -m 0755 -D %{SOURCE17} %{buildroot}%{_bindir}/nvidia-boot-update

# Choice of kernel module type:
install -p -m 0644 -D %{SOURCE18} %{buildroot}%{_sysconfdir}/nvidia/kernel.conf

# Nvidia modesetting support:
install -p -m 0644 -D %{SOURCE19} %{buildroot}%{_sysconfdir}/modprobe.d/nvidia-modeset.conf

# Load nvidia-uvm, enable complete power management:
install -p -m 0644 -D %{SOURCE20} %{buildroot}%{_modprobedir}/nvidia.conf

# Avoid Nvidia modules getting in the initrd:
install -p -m 0644 -D %{SOURCE24} %{buildroot}%{_dracut_conf_d}/99-nvidia.conf

# UDev rules
# https://github.com/NVIDIA/nvidia-modprobe/blob/master/modprobe-utils/nvidia-modprobe-utils.h#L33-L46
# https://github.com/negativo17/nvidia-kmod-common/issues/11
# https://github.com/negativo17/nvidia-driver/issues/27
install -p -m 644 -D %{SOURCE21} %{buildroot}%{_udevrulesdir}/60-nvidia.rules

# Firmware files:
mkdir -p %{buildroot}%{_prefix}/lib/firmware/nvidia/%{version}/
install -p -m 644 firmware/* %{buildroot}%{_prefix}/lib/firmware/nvidia/%{version}

%post
%{_bindir}/nvidia-boot-update post

%preun
if [ "$1" -eq "0" ]; then
  %{_bindir}/nvidia-boot-update preun
fi ||:

%files
%{_dracut_conf_d}/99-nvidia.conf
%{_modprobedir}/nvidia.conf
%dir %{_prefix}/lib/firmware
%dir %{_prefix}/lib/firmware/nvidia
%{_prefix}/lib/firmware/nvidia/%{version}
%{_bindir}/nvidia-boot-update
%config(noreplace) %{_sysconfdir}/modprobe.d/nvidia-modeset.conf
%config(noreplace) %{_sysconfdir}/nvidia/kernel.conf
%{_udevrulesdir}/60-nvidia.rules

%changelog
* Mon Sep 01 2025 Simone Caronni <negativo17@gmail.com> - 3:580.82.07-1
- Update to 580.82.07.

* Thu Aug 14 2025 Simone Caronni <negativo17@gmail.com> - 3:580.76.05-1
- Update to 580.76.05.

* Tue Aug 05 2025 Simone Caronni <negativo17@gmail.com> - 3:580.65.06-1
- Update to 580.65.06.

* Wed Jul 23 2025 Simone Caronni <negativo17@gmail.com> - 3:575.64.05-1
- Update to 575.64.05.

* Tue Jul 01 2025 Simone Caronni <negativo17@gmail.com> - 3:575.64.03-1
- Update to 575.64.03.

* Wed Jun 25 2025 Simone Caronni <negativo17@gmail.com> - 3:575.64-2
- Also blacklist nova-core.

* Wed Jun 18 2025 Simone Caronni <negativo17@gmail.com> - 3:575.64-1
- Update to 575.64.

* Thu May 29 2025 Simone Caronni <negativo17@gmail.com> - 3:575.57.08-1
- Update to 575.57.08.

* Tue May 20 2025 Simone Caronni <negativo17@gmail.com> - 3:575.51.02-1
- Update to 575.51.02.

* Tue May 20 2025 Simone Caronni <negativo17@gmail.com> - 3:570.153.02-1
- Update to 570.153.02.

* Tue Apr 22 2025 Simone Caronni <negativo17@gmail.com> - 3:570.144-1
- Update to 570.144.

* Wed Mar 19 2025 Simone Caronni <negativo17@gmail.com> - 3:570.133.07-1
- Update to 570.133.07.

* Mon Mar 10 2025 Simone Caronni <negativo17@gmail.com> - 3:570.124.04-2
- Move nvidia-boot-update to _bindir.

* Fri Feb 28 2025 Simone Caronni <negativo17@gmail.com> - 3:570.124.04-1
- Update to 570.124.04.

* Wed Feb 12 2025 Simone Caronni <negativo17@gmail.com> - 3:570.86.16-3
- Update nvidia-boot-update script.

* Wed Feb 12 2025 Simone Caronni <negativo17@gmail.com> - 3:570.86.16-2
- Also add a softep on nvidia-uvm, required for some GPUs.

* Fri Jan 31 2025 Simone Caronni <negativo17@gmail.com> - 3:570.86.16-1
- Update to 570.86.16.

* Mon Jan 27 2025 Simone Caronni <negativo17@gmail.com> - 3:570.86.15-1
- Update to 570.86.15.

* Wed Dec 25 2024 Simone Caronni <negativo17@gmail.com> - 3:565.77-2
- Run nvidia-modprobe only on add/bind (thanks os369510).

* Thu Dec 05 2024 Simone Caronni <negativo17@gmail.com> - 3:565.77-1
- Update to 565.77.

* Tue Oct 29 2024 Simone Caronni <negativo17@gmail.com> - 3:565.57.01-2
- Update power management configuration.

* Sat Oct 26 2024 Simone Caronni <negativo17@gmail.com> - 3:565.57.01-1
- Update to 565.57.01.

* Fri Oct 11 2024 Simone Caronni <negativo17@gmail.com> - 3:560.35.03-2
- Fix configuration file replacement (#14).

* Wed Sep 04 2024 Simone Caronni <negativo17@gmail.com> - 3:560.35.03-1
- Update to 560.35.03.
- Switch by default to open modules.

* Tue Jul 02 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58.02-1
- Update to 555.58.02.

* Fri Jun 28 2024 Simone Caronni <negativo17@gmail.com> - 3:555.58-1
- Update to 555.58.

* Wed Jun 05 2024 Simone Caronni <negativo17@gmail.com> - 3:550.90.07-1
- Update to 550.90.07.

* Fri May 31 2024 Simone Caronni <negativo17@gmail.com> - 3:550.78-2
- Fix typo in preun scriptlet.

* Fri Apr 26 2024 Simone Caronni <negativo17@gmail.com> - 3:550.78-1
- Update to 550.78.

* Thu Apr 18 2024 Simone Caronni <negativo17@gmail.com> - 3:550.76-1
- Update to 550.76.

* Sun Mar 24 2024 Simone Caronni <negativo17@gmail.com> - 3:550.67-1
- Update to 550.67.

* Mon Mar 11 2024 Simone Caronni <negativo17@gmail.com> - 3:550.54.14-2
- Add support for installing drivers without a configured bootloader (i.e.
  kickstart case).
- Add support for sdboot.

* Sun Mar 03 2024 Simone Caronni <negativo17@gmail.com> - 3:550.54.14-1
- Update to 550.54.14.

* Tue Feb 06 2024 Simone Caronni <negativo17@gmail.com> - 3:550.40.07-1
- Update to 550.40.07.
