<?php

require_once "php/imports.php";
require_once "php/html_getargs.php";

$getargs = new html_getargs();

// Read which day to cover
$tmin = $getargs->readTime('year', 'month', 'day', null, null, null, $const->yearMin, $const->yearMax);

$date_string = date("d M Y", $tmin['utc'] + 0.1);

// Fetch observatory activity history
function get_activity_history($tmin)
{
    global $const;
    $a = floor(($tmin['utc'] + 0.1) / 86400) * 86400 + 43200;
    $b = $a + 86400;
    $stmt = $const->db->prepare("
SELECT s.call_sign, s.hex_ident, MIN(s.generated_timestamp) AS t_min, MAX(s.generated_timestamp) AS t_max,
       COUNT(*) AS squitter_count
FROM adsb_squitters s
WHERE s.generated_timestamp BETWEEN :x AND :y
GROUP BY call_sign, hex_ident
ORDER BY MIN(generated_timestamp);");
    $stmt->bindParam(':x', $x, PDO::PARAM_STR, 64);
    $stmt->bindParam(':y', $y, PDO::PARAM_STR, 64);
    $stmt->execute(['x' => $a, 'y' => $b]);
    $items = $stmt->fetchAll();
    return $items;
}

// Get information about aircraft, by hex ident
function get_aircraft_info($hex_ident)
{
    global $const;
    $stmt = $const->db->prepare("
SELECT a.manufacturername AS manufacturer, a.model AS model, a.owner AS owner, a.operator AS operator
FROM aircraft_hex_codes a
WHERE a.hex_ident=:h;");
    $stmt->bindParam(':h', $h, PDO::PARAM_STR, 64);
    $stmt->execute(['h' => $hex_ident]);
    $items = $stmt->fetchAll();

    $output = [
        'manufacturer' => '',
        'model' => '',
        'operator' => '',
        'owner' => ''
    ];

    if (count($items) > 0) {
        $output = [
            'manufacturer' => $items[0]['manufacturer'],
            'model' => $items[0]['model'],
            'operator' => $items[0]['operator'],
            'owner' => $items[0]['owner']
        ];

    }

    return $output;
}

$items = get_activity_history($tmin);

// Extra formatting
$cssextra = <<<__HTML__
td { max-width: 200px; vertical-align: middle; }
__HTML__;

$pageInfo = [
    "pageTitle" => "ADS-B database: Aircraft seen on {$date_string}",
    "pageDescription" => "ADS-B database: Aircraft seen on {$date_string}",
    "activeTab" => "about",
    "teaserImg" => null,
    "cssextra" => $cssextra,
    "includes" => [],
    "linkRSS" => null,
    "options" => ["sideAdvert"]
];

$pageTemplate->header($pageInfo);

?>

    <p class="widetitle" id="dcf21">ADS-B database: Aircraft seen on <?php echo $date_string; ?></p>

    <div style="padding:4px;">
        <table class="stripy bordered bordered2">
            <thead>
            <tr>
                <td>Call sign</td>
                <td>Hex ident</td>
                <td>First seen</td>
                <td>Last seen</td>
                <td>Position fixes</td>
                <td>Operator</td>
                <td>Manufacturer</td>
                <td>Model</td>
            </tr>
            </thead>
            <tbody>
            <?php
            foreach ($items as $item):
                $extras = get_aircraft_info($item['hex_ident']);
                $aircraft_url = "aircraft_squitters.php?" .
                    "year={$tmin['year']}&month={$tmin['mc']}&day={$tmin['day']}" .
                    "&call_sign=" . htmlentities($item['call_sign']) .
                    "&hex_ident=" . htmlentities($item['hex_ident']);
                ?>
                <tr>
                    <td><a href="<?php echo $aircraft_url; ?>"><?php echo $item['call_sign']; ?></a></td>
                    <td><a href="<?php echo $aircraft_url; ?>"><?php echo $item['hex_ident']; ?></a></td>
                    <td><?php echo date("H:i:s", $item['t_min']); ?></td>
                    <td><?php echo date("H:i:s", $item['t_max']); ?></td>
                    <td style="text-align: right;"><?php echo $item['squitter_count']; ?></td>
                    <td><?php echo $extras['operator'] ? $extras['operator'] : $extras['owner']; ?></td>
                    <td><?php echo $extras['manufacturer']; ?></td>
                    <td><?php echo $extras['model']; ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>

<?php
$pageTemplate->footer($pageInfo);
