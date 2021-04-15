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
SELECT * FROM adsb_squitters s
WHERE s.generated_timestamp BETWEEN :x AND :y
ORDER BY s.generated_timestamp;");
    $stmt->bindParam(':x', $x, PDO::PARAM_STR, 64);
    $stmt->bindParam(':y', $y, PDO::PARAM_STR, 64);
    $stmt->execute(['x' => $a, 'y' => $b]);
    $items = $stmt->fetchAll();
    return $items;
}

$items = get_activity_history($tmin);

$pageInfo = [
    "pageTitle" => "ADS-B database: Squitters on {$date_string}",
    "pageDescription" => "ADS-B database: Squitters on {$date_string}",
    "fluid" => true,
    "activeTab" => "about",
    "teaserImg" => null,
    "cssextra" => null,
    "includes" => [],
    "linkRSS" => null,
    "options" => ["sideAdvert"]
];

$pageTemplate->header($pageInfo);

?>

    <p class="widetitle" id="dcf21">ADS-B database: Squitters on <?php echo $date_string; ?></p>

    <div style="padding:4px;">
        <table class="stripy bordered bordered2">
            <thead>
            <tr>
                <td>message_type</td>
                <td>transmission_type</td>
                <td>session_id</td>
                <td>aircraft_id</td>
                <td>hex_ident</td>
                <td>flight_id</td>
                <td>generated_timestamp</td>
                <td>logged_timestamp</td>
                <td>call_sign</td>
                <td>altitude</td>
                <td>ground_speed</td>
                <td>track</td>
                <td>lat</td>
                <td>lon</td>
                <td>vertical_rate</td>
                <td>squawk</td>
                <td>alert</td>
                <td>emergency</td>
                <td>spi</td>
                <td>is_on_ground</td>
                <td>parse_time</td>
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
                    <td><?php echo $item['message_type']; ?></td>
                    <td><?php echo $item['transmission_type']; ?></td>
                    <td><?php echo $item['session_id']; ?></td>
                    <td><?php echo $item['aircraft_id']; ?></td>
                    <td><a href="<?php echo $aircraft_url; ?>"><?php echo $item['hex_ident']; ?></a></td>
                    <td><?php echo $item['flight_id']; ?></td>
                    <td><?php echo date("H:i:s", $item['generated_timestamp']); ?></td>
                    <td><?php echo date("H:i:s", $item['logged_timestamp']); ?></td>
                    <td><a href="<?php echo $aircraft_url; ?>"><?php echo $item['call_sign']; ?></a></td>
                    <td><?php echo $item['altitude']; ?></td>
                    <td><?php echo $item['ground_speed']; ?></td>
                    <td><?php echo $item['track']; ?></td>
                    <td><?php echo $item['lat']; ?></td>
                    <td><?php echo $item['lon']; ?></td>
                    <td><?php echo $item['vertical_rate']; ?></td>
                    <td><?php echo $item['squawk']; ?></td>
                    <td><?php echo $item['alert']; ?></td>
                    <td><?php echo $item['emergency']; ?></td>
                    <td><?php echo $item['spi']; ?></td>
                    <td><?php echo $item['is_on_ground']; ?></td>
                    <td><?php echo date("H:i:s", $item['parsed_timestamp']); ?></td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>

<?php
$pageTemplate->footer($pageInfo);
