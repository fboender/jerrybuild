.PHONY: doc test example
PROG=jerrybuild

fake:
	# NOOP

test:
	cd test && python test.py

clean:
	rm -f *.rpm
	rm -f *.deb
	rm -f *.tar.gz
	rm -f *.zip
	rm -f README.html
	find ./ -name "*.pyc" -delete
	find ./ -name "__pycache__" -type d -delete
	rm -f example/gen_*

doc:
	markdown_py README.md > README.html

release_clean: clean
	#@if [ "$(shell git status --porcelain)" != "" ]; then echo "Repo not clean. Not building"; exit 1; fi

release: release_src release_deb release_rpm

release_src: release_clean doc
	@echo "Making release for version $(REL_VERSION)"

	@if [ -z "$(REL_VERSION)" ]; then echo "REL_VERSION required"; exit 1; fi

	# Cleanup
	rm -rf $(PROG)-$(REL_VERSION)

	# Prepare source
	umask 022
	mkdir $(PROG)-$(REL_VERSION)
	cp -ar src/* $(PROG)-$(REL_VERSION)/
	cp LICENSE $(PROG)-$(REL_VERSION)/
	cp README.md $(PROG)-$(REL_VERSION)/
	cp CHANGELOG.txt $(PROG)-$(REL_VERSION)/
	cp contrib/jerrybuild.man.1 $(PROG)-$(REL_VERSION)/

	# Bump version numbers
	find $(PROG)-$(REL_VERSION)/ -type f -print0 | xargs -0 sed -i "s/%%MASTER%%/$(REL_VERSION)/g" 

	# Create archives
	zip -q -r $(PROG)-$(REL_VERSION).zip $(PROG)-$(REL_VERSION)
	tar -czf $(PROG)-$(REL_VERSION).tar.gz  $(PROG)-$(REL_VERSION)

release_deb: release_clean doc
	@if [ -z "$(REL_VERSION)" ]; then echo "REL_VERSION required"; exit 1; fi

	# Cleanup
	rm -rf rel_deb

	umask 022
	mkdir -p rel_deb/usr/bin
	mkdir -p rel_deb/usr/lib/${PROG}
	mkdir -p rel_deb/usr/lib/${PROG}/mako
	mkdir -p rel_deb/usr/lib/${PROG}/yaml
	mkdir -p rel_deb/usr/share/doc/$(PROG)
	mkdir -p rel_deb/usr/share/man/man1
	mkdir -p rel_deb/var/lib/${PROG}
	mkdir -p rel_deb/var/lib/${PROG}/workspace
	mkdir -p rel_deb/var/lib/${PROG}/deploy_keys
	mkdir -p rel_deb/var/lib/${PROG}/jobs
	mkdir -p rel_deb/etc/${PROG}
	mkdir -p rel_deb/etc/${PROG}/jobs.d
	mkdir -p rel_deb/etc/init.d
	mkdir -p rel_deb/usr/share/man/man1

	# Copy the source to the release directory structure.
	cp README.md rel_deb/usr/share/doc/$(PROG)/
	cp README.html rel_deb/usr/share/doc/$(PROG)/
	cp CHANGELOG.txt rel_deb/usr/share/doc/$(PROG)/
	cp -r src/* rel_deb/usr/lib/${PROG}/
	ln -s ../lib/$(PROG)/jerrybuild rel_deb/usr/bin/jerrybuild
	cp -r contrib/debian/DEBIAN rel_deb/
	cp contrib/debian/jerrybuild.cfg rel_deb/etc/${PROG}/${PROG}.cfg
	cp -r contrib/debian/jobs.d rel_deb/etc/${PROG}/
	cp contrib/debian/copyright rel_deb/usr/share/doc/$(PROG)/
	cp contrib/debian/changelog rel_deb/usr/share/doc/$(PROG)/
	cp contrib/debian/jerrybuild.init.sysv5 rel_deb/etc/init.d/${PROG}
	gzip -9 rel_deb/usr/share/doc/$(PROG)/changelog
	cp -r contrib/jerrybuild.man.1 rel_deb/usr/share/man/man1/${PROG}.1
	gzip -9 rel_deb/usr/share/man/man1/jerrybuild.1

	chmod 650 rel_deb/etc/${PROG}/jobs.d
	find rel_deb/ -type f -print0 | xargs -0 chmod 644 
	find rel_deb/ -type d -print0 | xargs -0 chmod 755
	chmod 755 rel_deb/DEBIAN/postinst rel_deb/etc/init.d/${PROG}

	# Bump version numbers
	find rel_deb/ -type f -print0 | xargs -0 sed -i "s/%%MASTER%%/$(REL_VERSION)/g" 

	# Create debian pacakge
	fakeroot dpkg-deb --build rel_deb > /dev/null
	mv rel_deb.deb $(PROG)-$(REL_VERSION).deb

	# Cleanup
	rm -rf rel_deb
	rm -rf $(PROG)-$(REL_VERSION)

	# Lint
	lintian *.deb

release_rpm: release_clean release_deb
	alien -r -g $(PROG)-$(REL_VERSION).deb
	sed -i '\:%dir "/":d' $(PROG)-$(REL_VERSION)/$(PROG)-$(REL_VERSION)-2.spec
	sed -i '\:%dir "/usr/":d' $(PROG)-$(REL_VERSION)/$(PROG)-$(REL_VERSION)-2.spec
	sed -i '\:%dir "/usr/share/":d' $(PROG)-$(REL_VERSION)/$(PROG)-$(REL_VERSION)-2.spec
	sed -i '\:%dir "/usr/share/man/":d' $(PROG)-$(REL_VERSION)/$(PROG)-$(REL_VERSION)-2.spec
	sed -i '\:%dir "/usr/share/man/man1/":d' $(PROG)-$(REL_VERSION)/$(PROG)-$(REL_VERSION)-2.spec
	sed -i '\:%dir "/usr/lib/":d' $(PROG)-$(REL_VERSION)/$(PROG)-$(REL_VERSION)-2.spec
	sed -i '\:%dir "/usr/bin/":d' $(PROG)-$(REL_VERSION)/$(PROG)-$(REL_VERSION)-2.spec
	cd $(PROG)-$(REL_VERSION) && rpmbuild --buildroot='$(shell readlink -f $(PROG)-$(REL_VERSION))/' -bb --target noarch '$(PROG)-$(REL_VERSION)-2.spec'


install: clean
	install -m 0755 -d \
		$(DESTDIR)/etc/jobs.d \
		$(DESTDIR)/lib/$(PROG)/tools \
		$(DESTDIR)/lib/$(PROG)/providers \
		$(DESTDIR)/lib/$(PROG)/static/font-awesome/css \
		$(DESTDIR)/lib/$(PROG)/static/font-awesome/fonts \
		$(DESTDIR)/lib/$(PROG)/static/css \
		$(DESTDIR)/lib/$(PROG)/views/helpers \
		$(DESTDIR)/share/doc \
		$(DESTDIR)/bin
	install -m 0755 src/*.py src/jerrybuild $(DESTDIR)/lib/$(PROG)/
	install -m 0755 src/tools/* $(DESTDIR)/lib/$(PROG)/tools
	install -m 0644 src/providers/*.py $(DESTDIR)/lib/$(PROG)/providers
	install -m 0644 src/static/font-awesome/css/*.css $(DESTDIR)/lib/$(PROG)/static/font-awesome/css
	install -m 0644 src/static/font-awesome/fonts/* $(DESTDIR)/lib/$(PROG)/static/font-awesome/fonts 
	install -m 0644 src/views/*.tpl $(DESTDIR)/lib/$(PROG)/views
	install -m 0644 src/views/helpers/*.tpl $(DESTDIR)/lib/$(PROG)/views/helpers
	install -m 0644 src/providers/*.py $(DESTDIR)/lib/$(PROG)/providers
	install -m 0644 src/static/css/*.css $(DESTDIR)/lib/$(PROG)/static/css
	install -m 0644 CHANGELOG.txt README.md $(DESTDIR)/share/doc/
	install -m 0644 jerrybuild.cfg.example $(DESTDIR)/etc/jerrybuild.cfg.dist
	ln -nsf $(DESTDIR)/lib/$(PROG)/jerrybuild $(DESTDIR)/bin/jerrybuild

uninstall:
	rm -rf /usr/local/lib/$(PROG)
	rm -f /usr/local/man/man/ansible-cmdb.man.1.gz
	rm -rf /usr/local/bin/ansible-cmdb
