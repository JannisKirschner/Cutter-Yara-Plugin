$cutter_location = "C:\Path\To\Cutter-Dir\python36\"

py -m pip install yara-python
$plugin_info = py -m pip show yara-python
$plugin_location = $plugin_info | Where-Object {$_ | Select-String "Location: "}
$location_header, $plugin_location = $plugin_location.Split(" ")
$files = Get-ChildItem -Path "$plugin_location"

$pydfile = Get-ChildItem -Path "$plugin_location" -Filter "yara*.pyd" | Select-Object -expandproperty fullname
$distfiles = Get-ChildItem -Path "$plugin_location" -Filter "yara*dist-info" | Select-Object -expandproperty fullname

copy-item -Path $pydfile -Destination "$cutter_location"
copy-item -Path $distfiles -Destination "$cutter_location\site-packages"