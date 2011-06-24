#(c) ylmf 2011/6 <hechao @115.com>

PREFIX = /usr
LIBDIR = $(PREFIX)/lib

.PHONY : install
.PHONY : uninstall

all:
	@echo "Makefile: Available actions: install, uninstall,"
	@echo "Makefile: Available variables: PREFIX, DESTDIR"
	
# install
install:
	python -u local.py
	install -d $(DESTDIR)$(PREFIX)/share/dbus-1/system-services $(DESTDIR)/etc/dbus-1/system.d \
	           $(DESTDIR)$(PREFIX)/share/polkit-1/actions $(DESTDIR)$(LIBDIR) $(DESTDIR)$(PREFIX)/share \
		   $(DESTDIR)$(PREFIX)/bin/ $(DESTDIR)$(PREFIX)/share/applications/  $(DESTDIR)$(PREFIX)/share/pixmaps
	-cp -r src/dbus/com.ylmf.yinst.service $(DESTDIR)$(PREFIX)/share/dbus-1/system-services
	-cp -r src/dbus/com.ylmf.yinst.conf $(DESTDIR)/etc/dbus-1/system.d
	-cp -r src/dbus/com.ylmf.yinst.policy $(DESTDIR)$(PREFIX)/share/polkit-1/actions
	-cp -r src/lib/yinst4linux $(DESTDIR)$(LIBDIR)
	-cp -r src/lib/yinst4linux $(DESTDIR)$(PREFIX)/share/pixmaps/
	-cp -r src/share/locale $(DESTDIR)$(PREFIX)/share
	-install src/bin/yinst $(DESTDIR)$(PREFIX)/bin/
	-install src/bin/yinst4linux.desktop $(DESTDIR)$(PREFIX)/share/applications/
	
	@echo "Makefile: yinst installed."


# uninstall
uninstall:
	rm -vf $(DESTDIR)$(PREFIX)/share/dbus-1/system-services/com.ylmf.yinst.service
	rm -vf $(DESTDIR)/etc/dbus-1/system.d/com.ylmf.yinst.conf
	rm -vf $(DESTDIR)$(PREFIX)/share/polkit-1/actions/com.ylmf.yinst.policy
	rm -rf $(DESTDIR)$(LIBDIR)/yinst
	rm -rf $(DESTDIR)$(PREFIX)/share/applications/yinst.desktop
	rm -rf $(DESTDIR)$(PREFIX)/bin/yinst
	rm -vf $(DESTDIR)/etc/grub.d/05_livecd
	rm -rf ~/.yinst
	update-grub
	


