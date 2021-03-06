# Lyle Scott, III
# lyle@digitalfoo.net

FILE_DIR = $(HOME)/.connect-to_indicator
DEFAULT_TERMINAL = /usr/bin/gnome-terminal
DEFAULT_RDPAPP = /usr/bin/rdesktop
DEFAULT_VNCAPP = /usr/bin/vncviewer
AUTOSTART_FILE = ~/.config/autostart/connect-to_indicator.desktop


default: usage

usage: 
	@echo USAGE: 
	@echo make
	@echo make install \(includes autostart_on\)
	@echo make uninstall \(includes autostart_off\)
	@echo make autostart_on
	@echo make autostart_off
	@echo make config
	@echo make installconfig
	@echo make clean

install: installconfig autostart_on
	@mkdir -p $(FILE_DIR)
	@echo 'connect-to_indicator.py.dist --> connect-to_indicator.py'
	@cp -i connect-to_indicator.py.dist connect-to_indicator.py
	@sed -i "s|__FILE_DIR__|$(FILE_DIR)|" connect-to_indicator.py
	@cp -i README *.py *.sh icon.png $(FILE_DIR)
	@chmod +x $(FILE_DIR)/connect-to_indicator.py
	@echo ''
	@echo Enable autostart \(via gnome-session\):
	@echo make autostart_on  
	@echo '' 
	@nohup python $(FILE_DIR)/connect-to_indicator.py &
	@echo 'Done. Installed to: $(FILE_DIR)' 

uninstall: autostart_off
	@rm -i $(FILE_DIR)/*
	@rm -ir $(FILE_DIR)

autostart_on:
	@mkdir -p ~/.config/autostart/
	@echo 'connect-to_indicator.desktop.dist --> connect-to_indicator.desktop' 
	@cp -i connect-to_indicator.desktop.dist connect-to_indicator.desktop
	@sed -i "s|__FILE_DIR__|$(FILE_DIR)|" connect-to_indicator.desktop
	@echo 'connect-to_indicator.desktop --> ~/.config/autostart/' 
	@cp -i connect-to_indicator.desktop ~/.config/autostart/
	@echo autostart toggled ON

autostart_off:
	@test ! -f $(AUTOSTART_FILE) || rm $(AUTOSTART_FILE)
	@echo autostart toggled OFF

config: 
	@echo "config.xml.dist --> config.xml"
	@cp -i config.xml.dist config.xml
	@sed -i "s|__FILE_DIR__|$(FILE_DIR)|" config.xml
	@sed -i "s|__DEFAULT_TERMINAL__|$(DEFAULT_TERMINAL)|" config.xml
	@sed -i "s|__DEFAULT_RDPAPP__|$(DEFAULT_RDPAPP)|" config.xml
	@sed -i "s|__DEFAULT_VNCAPP__|$(DEFAULT_VNCAPP)|" config.xml
	@echo Config generated:
	@echo `pwd`/config.xml

installconfig: config
	@mkdir -p $(FILE_DIR)
	@echo Installing config.xml to $(FILE_DIR)/config.xml
	@cp -i config.xml $(FILE_DIR)/config.xml

runonce: config
	@echo Look in the indicator section on the top gnome bar...
	@sed -i "s|$(FILE_DIR)|`pwd`|" config.xml
	@cp connect-to_indicator.py.dist connect-to_indicator.py
	@sed -i "s|__FILE_DIR__|`pwd`|" connect-to_indicator.py
	@python connect-to_indicator.py

clean:
	rm -f config.xml connect-to_indicator.desktop connect-to_indicator.py nohup.out
