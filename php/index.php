<?php

require "php/imports.php";

$pageInfo = [
    "pageTitle" => "ADS-B database",
    "pageDescription" => "ADS-B database",
    "activeTab" => "about",
    "teaserImg" => null,
    "cssextra" => null,
    "includes" => [],
    "linkRSS" => null,
    "options" => ["sideAdvert"]
];

$pageTemplate->header($pageInfo);

?>

    <p class="widetitle" id="dcf21">ADS-B database</p>

    <p class="widetitle">Contact details</p>

    <div class="newsbody">
        <p>
            You can email me at
            <img style="vertical-align:middle;"
                 src="<?php echo $const->server; ?>images/email2.png" alt="root@127.0.0.1"/>.
        </p>
    </div>

<?php
$pageTemplate->footer($pageInfo);
