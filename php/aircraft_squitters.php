<?php

require_once "php/imports.php";
require_once "php/html_getargs.php";

$getargs = new html_getargs();

// Read which day to cover
$tmin = $getargs->readTime('year', 'month', 'day', null, null, null, $const->yearMin, $const->yearMax);

// Fetch identity of aircraft we are to display data for
$call_sign = "";
$hex_ident = "";
if (array_key_exists("call_sign", $_GET) && is_string($_GET["call_sign"])) $call_sign = $_GET["call_sign"];
if (array_key_exists("hex_ident", $_GET) && is_string($_GET["hex_ident"])) $hex_ident = $_GET["hex_ident"];
$aircraft_string = htmlentities($call_sign) . "/" . htmlentities($hex_ident);

$date_string = date("d M Y", $tmin['utc'] + 0.1);

// Fetch observatory activity history
function get_activity_history($tmin, $call_sign, $hex_ident)
{
    global $const;
    $a = floor(($tmin['utc'] + 0.1) / 86400) * 86400;
    $b = $a + 86400;
    $stmt = $const->db->prepare("
SELECT * FROM adsb_squitters s
WHERE s.generated_timestamp BETWEEN :x AND :y
    AND s.call_sign=:c AND s.hex_ident=:h
ORDER BY s.generated_timestamp;");
    $stmt->bindParam(':x', $x, PDO::PARAM_STR, 64);
    $stmt->bindParam(':y', $y, PDO::PARAM_STR, 64);
    $stmt->bindParam(':c', $c, PDO::PARAM_STR, 64);
    $stmt->bindParam(':h', $h, PDO::PARAM_STR, 64);
    $stmt->execute(['x' => $a, 'y' => $b, 'c' => $call_sign, 'h' => $hex_ident]);
    $items = $stmt->fetchAll();
    return $items;
}

$items = get_activity_history($tmin, $call_sign, $hex_ident);

$pageInfo = [
    "pageTitle" => "ADS-B database: Squitters by {$aircraft_string} on {$date_string}",
    "pageDescription" => "ADS-B database: Squitters by {$aircraft_string} on {$date_string}",
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

    <p class="widetitle" id="dcf21">
        ADS-B database: Squitters by <?php echo $aircraft_string; ?> on <?php echo $date_string; ?>
    </p>

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
                ?>
                <tr>
                    <td><?php echo $item['message_type']; ?></td>
                    <td><?php echo $item['transmission_type']; ?></td>
                    <td><?php echo $item['session_id']; ?></td>
                    <td><?php echo $item['aircraft_id']; ?></td>
                    <td><?php echo $item['hex_ident']; ?></td>
                    <td><?php echo $item['flight_id']; ?></td>
                    <td><?php echo date("H:i:s", $item['generated_timestamp']); ?></td>
                    <td><?php echo date("H:i:s", $item['logged_timestamp']); ?></td>
                    <td><?php echo $item['call_sign']; ?></td>
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
