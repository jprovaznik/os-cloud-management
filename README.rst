===============================
os-cloud-management
===============================

Management for OpenStack clouds.

* start a new update in interactive mode:

  ``stack-update -s overcloud -t templates/update.yaml -i``

* scale out compute nodes in Overcloud:

  ``stack-scale -s 483e364a-2752-498c-b987-44b5a9b4dc6a -p 99c08fda-0d0c-46e9-a82f-2e07a226f3e1 -n 2 -r Compute-1``
