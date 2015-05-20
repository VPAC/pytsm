%if 0%{?fedora} > 12
%global with_python3 1
%else
%{!?__python2: %global __python2 /usr/bin/python2}
%{!?python2_sitelib: %global python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}
%endif

%global srcname python-pytsm

Name: python-pytsm
Version: 0.0.3
Release: 1%{?dist}
Summary: Small Python 2 library to monitor TSM
Requires: python-pytsm-common, python(abi) = 2.7

Group: Development/Libraries
License: GPLv3+
Url: https://github.com/VPAC/pytsm/
Source: %{name}_%{version}.tar.gz

BuildArch: noarch
BuildRequires:  python2-devel, python-setuptools, python-six
%if 0%{?fedora} > 20
BuildRequires:  python-flake8
%endif # if fedora > 20
%if 0%{?with_python3}
BuildRequires:  python3-devel, python3-setuptools, python3-six
%if 0%{?fedora} > 20
BuildRequires:  python3-flake8
%endif # fedora > 20
%endif # if with_python3

%description
Contains Python 2 TSM bindings.


%package -n python-pytsm-common
Summary: Common files for small Python 3 library to monitor TSM

%description -n python-pytsm-common
Contains common files for Python 3 TSM bindings.

%changelog
* Wed May 20 2015 Brian May <brian@microcomaustralia.com.au> 0.0.3-1
- updates to rpm spec file.


%if 0%{?with_python3}
%package -n python3-pytsm
Summary: Small Python 3 library to monitor TSM
Requires: python-pytsm-common

%description -n python3-pytsm
Contains Python 3 TSM bindings.
%endif # with_python3

%prep
%setup -q

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
%if 0%{?fedora} > 20
    %{__python2} /usr/bin/flake8 .
%endif # fedora > 20
%{__python2} setup.py test

%if 0%{?with_python3}
%if 0%{?fedora} > 20
    %{__python3} /usr/bin/flake8 .
%endif # fedora > 20
%{__python3} setup.py test
%endif # with_python3

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{python2_sitelib}/*
%doc COPYING.txt README.rst

%files -n python-pytsm-common
%{_bindir}/pytsm
%doc COPYING.txt README.rst

%if 0%{?with_python3}
%files -n python3-pytsm
%{python3_sitelib}/*
%doc COPYING.txt README.rst
%endif # with_python3
