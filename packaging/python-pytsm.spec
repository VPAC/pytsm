%if 0%{?fedora} > 12
%global with_python3 1
%else
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%endif

%global srcname python-pytsm

Name: python-pytsm
Version: 0.0.2
Release: 1%{?dist}
Summary: Small Python 2 library to monitor TSM
Requires: python-pytsm-common, python(abi) = 2.7

Group: Development/Libraries
License: GPL3+
Url: https://github.com/VPAC/pytsm/

Source0: %{name}_%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
BuildRequires:  python2-devel, python-setuptools, python-six
%if 0%{?with_python3}
BuildRequires:  python3-devel, python3-setuptools, python3-six, python3-flake8
%endif # if with_python2

%description
Contains Python 2 TSM bindings.


%package -n python-pytsm-common
Summary: Common files for small Python 3 library to monitor TSM

%description -n python-pytsm-common
Contains common files for Python 3 TSM bindings.


%if 0%{?with_python3}
%package -n python3-pytsm
Summary: Small Python 3 library to monitor TSM
Requires: python-pytsm-common

%description -n python3-pytsm
Contains Python 3 TSM bindings.
%endif # with_python2

%prep

%build
%{__python2} setup.py build

%if 0%{?with_python3}
%{__python3} setup.py build
%endif # with_python3

%install
rm -rf %{buildroot}

%{__python2} setup.py install  --skip-build --root $RPM_BUILD_ROOT

%if 0%{?with_python3}
%{__python3} setup.py install --skip-build --root $RPM_BUILD_ROOT
%endif # with_python3

cp debian/pytsm $RPM_BUILD_ROOT%{_bindir}/pytsm
chmod 755 $RPM_BUILD_ROOT%{_bindir}/pytsm
sed -i 's=python2.7=python=' $RPM_BUILD_ROOT%{_bindir}/pytsm
sed -i 's=/usr/lib/python2.7/dist-packages/pytsm=%{python2_sitelib}=' $RPM_BUILD_ROOT%{_bindir}/pytsm
%if 0%{?with_python3}
sed -i 's=/usr/lib/python3/dist-packages=%{python3_sitelib}=' $RPM_BUILD_ROOT%{_bindir}/pytsm
%endif # with_python3

%check
#%{__python2} /usr/bin/flake8 .
%{__python2} setup.py test

%if 0%{?with_python3}
%{__python2} /usr/bin/flake8 .
%{__python3} setup.py test
%endif # with_python3

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{python2_sitelib}/*

%files -n python-pytsm-common
%{_bindir}/pytsm

%if 0%{?with_python3}
%files -n python3-pytsm
%{python3_sitelib}/*
%endif # with_python3
