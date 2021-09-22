%if 0%{?rhel} == 7
%global _dracutopts     nouveau.modeset=0 rd.driver.blacklist=nouveau nvidia-drm.modeset=1
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal
%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d
%global _modprobedir    %{_prefix}/lib/modprobe.d/
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL
%endif

%if 0%{?fedora} || 0%{?rhel} >= 8
%global _dracutopts     rd.driver.blacklist=nouveau
# Don't disable nouveau at boot. Just matching the driver with OutputClass in
# the X.org configuration is enough to load the whole Nvidia stack or the Mesa
# one:
%global _dracutopts_rm  nomodeset gfxpayload=vga=normal nouveau.modeset=0 nvidia-drm.modeset=1
%global _dracut_conf_d  %{_prefix}/lib/dracut/dracut.conf.d
%global _grubby         %{_sbindir}/grubby --update-kernel=ALL
%endif

# gsp.bin: ELF 64-bit LSB executable, UCB RISC-V
%global _binaries_in_noarch_packages_terminate_build 0

Name:           nvidia-kmod-common
Version:        470.74
Release:        1%{?dist}
Summary:        Common file for NVIDIA's proprietary driver kernel modules
Epoch:          3
License:        NVIDIA License
URL:            http://www.nvidia.com/object/unix.html

BuildArch:      noarch

Source0:        %{name}-%{version}.tar.xz
Source19:       nvidia.conf.etc
Source20:       nvidia.conf
Source21:       60-nvidia.rules
Source24:       99-nvidia.conf

# UDev rule location (_udevrulesdir) and systemd macros:
%if 0%{?fedora}
BuildRequires:  systemd-rpm-macros
%else
BuildRequires:  systemd
%endif

Requires:       grubby
Requires:       linux-firmware
Requires:       nvidia-kmod = %{?epoch:%{epoch}:}%{version}
Provides:       nvidia-kmod-common = %{?epoch:%{epoch}:}%{version}
Obsoletes:      cuda-nvidia-kmod-common

%description
This package provides the common files required by all NVIDIA kernel module
package variants.
 
%prep
%autosetup

%install
mkdir -p %{buildroot}%{_udevrulesdir}
mkdir -p %{buildroot}%{_modprobedir}/
mkdir -p %{buildroot}%{_dracut_conf_d}/
mkdir -p %{buildroot}%{_prefix}/lib/firmware/nvidia/%{version}/

%if 0%{?fedora} >= 35
# Nvidia modesetting support
install -p -m 0644 -D %{SOURCE19} %{buildroot}%{_sysconfdir}/modprobe.d/nvidia.conf
%endif

# Blacklist nouveau and load nvidia-uvm:
install -p -m 0644 %{SOURCE20} %{buildroot}%{_modprobedir}/

# Avoid Nvidia modules getting in the initrd:
install -p -m 0644 %{SOURCE24} %{buildroot}%{_dracut_conf_d}/

# UDev rules:
# https://github.com/NVIDIA/nvidia-modprobe/blob/master/modprobe-utils/nvidia-modprobe-utils.h#L33-L46
# https://github.com/negativo17/nvidia-driver/issues/27
install -p -m 644 %{SOURCE21} %{buildroot}%{_udevrulesdir}

# Firmware files
install -p -m 644 firmware/* %{buildroot}%{_prefix}/lib/firmware/nvidia/%{version}

%post
%{_grubby} --args='%{_dracutopts}' --remove-args='%{_dracutopts_rm}' &>/dev/null
if [ ! -f /run/ostree-booted ]; then
  . %{_sysconfdir}/default/grub
  if [ -z "${GRUB_CMDLINE_LINUX}" ]; then
    echo GRUB_CMDLINE_LINUX="%{_dracutopts}" >> %{_sysconfdir}/default/grub
  else
    for param in %{_dracutopts}; do
      echo ${GRUB_CMDLINE_LINUX} | grep -q $param
      [ $? -eq 1 ] && GRUB_CMDLINE_LINUX="${GRUB_CMDLINE_LINUX} ${param}"
    done
    for param in %{_dracutopts_rm}; do
      echo ${GRUB_CMDLINE_LINUX} | grep -q $param
      [ $? -eq 0 ] && GRUB_CMDLINE_LINUX="$(echo ${GRUB_CMDLINE_LINUX} | sed -e "s/$param//g")"
    done
    sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
  fi
fi

%preun
if [ "$1" -eq "0" ]; then
  %{_grubby} --remove-args='%{_dracutopts}' &>/dev/null
  if [ ! -f /run/ostree-booted ]; then
    for param in %{_dracutopts}; do
      echo ${GRUB_CMDLINE_LINUX} | grep -q $param
      [ $? -eq 0 ] && GRUB_CMDLINE_LINUX="$(echo ${GRUB_CMDLINE_LINUX} | sed -e "s/$param//g")"
    done
    sed -i -e "s|^GRUB_CMDLINE_LINUX=.*|GRUB_CMDLINE_LINUX=\"${GRUB_CMDLINE_LINUX}\"|g" %{_sysconfdir}/default/grub
  fi
fi ||:

%files
%{_dracut_conf_d}/99-nvidia.conf
%{_modprobedir}/nvidia.conf
%{_prefix}/lib/firmware/nvidia/%{version}
%if 0%{?fedora} >= 35
%config %{_sysconfdir}/modprobe.d/nvidia.conf
%endif
%{_udevrulesdir}/60-nvidia.rules

%changelog
* Tue Sep 21 2021 Simone Caronni <negativo17@gmail.com> - 3:470.74-1
- Update to 470.74.

* Fri Aug 20 2021 Simone Caronni <negativo17@gmail.com> - 3:470.63.01-3
- SPEC file cleanup.
- Enable modesetting by default for Fedora 35+

* Fri Aug 20 2021 Simone Caronni <negativo17@gmail.com> - 3:470.63.01-2
- Enable complete power management.

* Wed Aug 11 2021 Simone Caronni <negativo17@gmail.com> - 3:470.63.01-1
- Update to 470.63.01.

* Tue Jul 20 2021 Simone Caronni <negativo17@gmail.com> - 3:470.57.02-1
- Update to 470.57.02.

* Mon Jun 07 2021 Simone Caronni <negativo17@gmail.com> - 3:460.84-1
- Update to 460.84.

* Wed May 12 2021 Simone Caronni <negativo17@gmail.com> - 3:460.80-1
- Update to 460.80.

* Sun Apr 18 2021 Simone Caronni <negativo17@gmail.com> - 3:460.73.01-1
- Update to 460.73.01.

* Fri Mar 19 2021 Simone Caronni <negativo17@gmail.com> - 3:460.67-1
- Update to 460.67.

* Mon Mar 01 2021 Simone Caronni <negativo17@gmail.com> - 3:460.56-1
- Update to 460.56.

* Wed Jan 27 2021 Simone Caronni <negativo17@gmail.com> - 3:460.39-1
- Update to 460.39.

* Thu Jan  7 2021 Simone Caronni <negativo17@gmail.com> - 3:460.32.03-1
- Update to 460.32.03.

* Sun Dec 20 2020 Simone Caronni <negativo17@gmail.com> - 3:460.27.04-1
- Update to 460.27.04.
- Update comments in modprobe file.

* Mon Dec 07 2020 Simone Caronni <negativo17@gmail.com> - 3:450.80.02-2
- Remove CentOS/RHEL 6 support.

* Tue Oct 06 2020 Simone Caronni <negativo17@gmail.com> - 3:450.80.02-1
- Update to 450.80.02.

* Thu Aug 20 2020 Simone Caronni <negativo17@gmail.com> - 3:450.66-1
- Update to 450.66.

* Fri Jul 10 2020 Simone Caronni <negativo17@gmail.com> - 3:450.57-1
- Update to 450.57.

* Thu Jun 25 2020 Simone Caronni <negativo17@gmail.com> - 3:440.100-1
- Update to 440.100.

* Thu Apr 09 2020 Simone Caronni <negativo17@gmail.com> - 3:440.82-1
- Update to 440.82.

* Fri Feb 28 2020 Simone Caronni <negativo17@gmail.com> - 3:440.64-1
- Update to 440.64.

* Tue Feb 04 2020 Simone Caronni <negativo17@gmail.com> - 3:440.59-1
- Update to 440.59.

* Sat Dec 14 2019 Simone Caronni <negativo17@gmail.com> - 3:440.44-1
- Update to 440.44.

* Sat Nov 30 2019 Simone Caronni <negativo17@gmail.com> - 3:440.36-1
- Update to 440.36.

* Mon Nov 11 2019 Simone Caronni <negativo17@gmail.com> - 3:440.31-2
- Fix udev rules synax (thanks Leigh)

* Sat Nov 09 2019 Simone Caronni <negativo17@gmail.com> - 3:440.31-1
- Update to 440.31.

* Thu Oct 17 2019 Simone Caronni <negativo17@gmail.com> - 3:440.26-1
- Update to 440.26.

* Tue Oct 01 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-3
- Remove workaround for onboard GPU devices.
- Fix typo on udev character device rules (thanks tbaederr).

* Tue Oct 01 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-2
- Fix build on CentOS/RHEL 8

* Tue Sep 03 2019 Simone Caronni <negativo17@gmail.com> - 3:435.21-1
- Update to 435.21.

* Thu Aug 22 2019 Simone Caronni <negativo17@gmail.com> - 3:435.17-1
- Update to 435.17.
- Add power management functions as per documentation.
- Require systemd-rpm-macros instead of systemd on Fedora/RHEL 8+.

* Wed Jul 31 2019 Simone Caronni <negativo17@gmail.com> - 3:430.40-1
- Update to 430.40.

* Fri Jul 12 2019 Simone Caronni <negativo17@gmail.com> - 3:430.34-1
- Update to 430.34.

* Wed Jun 12 2019 Simone Caronni <negativo17@gmail.com> - 3:430.26-1
- Update to 430.26.

* Thu Jun 06 2019 Simone Caronni <negativo17@gmail.com> - 3:430.14-2
- Do not run post/preun scriptlets on Atomic/Silverblue.

* Sat May 18 2019 Simone Caronni <negativo17@gmail.com> - 3:430.14-1
- Update to 430.14.

* Thu May 09 2019 Simone Caronni <negativo17@gmail.com> - 3:418.74-1
- Update to 418.74.
- Remove fallback scenario (thanks Karol Herbst).

* Thu Apr 18 2019 Simone Caronni <negativo17@gmail.com> - 3:418.56-2
- Obsoletes cuda-nvidia-kmod-common (thanks Timm).

* Sun Mar 24 2019 Simone Caronni <negativo17@gmail.com> - 3:418.56-1
- Update to 418.56.

* Fri Feb 22 2019 Simone Caronni <negativo17@gmail.com> - 3:418.43-1
- Update to 418.43.

* Wed Feb 06 2019 Simone Caronni <negativo17@gmail.com> - 3:418.30-1
- Update to 418.30.

* Sun Feb 03 2019 Simone Caronni <negativo17@gmail.com> - 3:415.27-1
- First build.
