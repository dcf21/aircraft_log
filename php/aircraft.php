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
SELECT call_sign, hex_ident, MIN(generated_timestamp) AS t_min, MAX(generated_timestamp) AS t_max,
       COUNT(*) AS squitter_count
FROM adsb_squitters s
WHERE s.generated_timestamp BETWEEN :x AND :y
GROUP BY call_sign, hex_ident
ORDER BY s.generated_timestamp;");
    $stmt->bindParam(':x', $x, PDO::PARAM_STR, 64);
    $stmt->bindParam(':y', $y, PDO::PARAM_STR, 64);
    $stmt->execute(['x' => $a, 'y' => $b]);
    $items = $stmt->fetchAll();
    return $items;
}

$items = get_activity_history($tmin);

$pageInfo = [
    "pageTitle" => "ADS-B database: Aircraft seen on {$date_string}",
    "pageDescription" => "ADS-B database: Aircraft seen on {$date_string}",
    "activeTab" => "about",
    "teaserImg" => null,
    "cssextra" => null,
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
            </tr>
            </thead>
            <tbody>
            <?php
            foreach ($items as $item):
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
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>

<?php
$pageTemplate->footer($pageInfo);
