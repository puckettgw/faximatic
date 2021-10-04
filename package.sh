zip -jr inbound_fax.zip build.sh inbound_fax.py requirements.txt
fission package delete --name inboundfax-package
fission package create --name inboundfax-package --sourcearchive inbound_fax.zip --env python-faximatic --buildcmd "./build.sh"
fission function update --name inbound-fax --pkg inboundfax-package --entrypoint "inbound_fax.main"
