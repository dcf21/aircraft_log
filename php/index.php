<?php

require_once "php/imports.php";
require_once "php/html_getargs.php";

$getargs = new html_getargs();

// Read which month to cover
$tmin = $getargs->readTime('year', 'month', null, null, null, null, $const->yearMin, $const->yearMax);

// Clip requested month to span over which we have data
if (
    ($tmin['year'] > intval(date('Y', $const->obs_latest))) ||
    (
        ($tmin['year'] == intval(date('Y', $const->obs_latest))) &&
        ($tmin['mc'] > intval(date('m', $const->obs_latest))))
) {
    $utc = mktime(0, 0, 1, date('m', $const->obs_latest), 1, date('Y', $const->obs_latest));
    $tmin = $getargs->readTimeFromUTC($utc);
}

if (
    ($tmin['year'] < intval(date('Y', $const->obs_earliest))) ||
    (
        ($tmin['year'] == intval(date('Y', $const->obs_earliest))) &&
        ($tmin['mc'] < intval(date('m', $const->obs_earliest))))
) {
    $utc = mktime(0, 0, 1, date('m', $const->obs_earliest), 1, date('Y', $const->obs_earliest));
    $tmin = $getargs->readTimeFromUTC($utc);
}

// Look up calendar date of start date
$month_name = date('F Y', $tmin['utc'] + 1);
$month = date('n', $tmin['utc'] + 1);
$year = date('Y', $tmin['utc'] + 1);

// Look up which months to put on the "prev" and "next" buttons
$prev_month = date('n', $tmin['utc'] - 10 * 24 * 3600);
$prev_month_year = date('Y', $tmin['utc'] - 10 * 24 * 3600);
$next_month = date('n', $tmin['utc'] + 40 * 24 * 3600);
$next_month_year = date('Y', $tmin['utc'] + 40 * 24 * 3600);

$days_in_month = date('t', $tmin['utc'] + 1);
$day_offset = date('w', $tmin['utc'] + 1);
$period = 24 * 3600;

$byday = [];

// Fetch observatory activity history
function get_activity_history($count_by, $suffix, $url)
{
    global $byday, $const, $tmin, $period, $days_in_month, $year, $month;
    $count = 0;
    while ($count < $days_in_month) {
        $a = floor($tmin['utc'] / 86400) * 86400 + 43200 + $period * $count;
        $b = $a + $period;
        $count++;
        $stmt = $const->db->prepare("
SELECT COUNT({$count_by}) AS result_count FROM adsb_squitters s
WHERE s.generated_timestamp BETWEEN :x AND :y;");
        $stmt->bindParam(':x', $x, PDO::PARAM_STR, 64);
        $stmt->bindParam(':y', $y, PDO::PARAM_STR, 64);
        $stmt->execute(['x' => $a, 'y' => $b]);
        $items = $stmt->fetchAll()[0]['result_count'];
        if ($items > 0) {
            $text = "<div style='height:55px;'>" .
                "<a href='{$url}?year={$year}&month={$month}&day={$count}'>" .
                "<span class='cal_number'>{$items}</span><span class='cal_type'>{$suffix}</span></a></div>";
        } else {
            $text = "";
        }
        $byday[$count][] = $text;
    }
}

get_activity_history("DISTINCT call_sign, hex_ident", " aircraft", "aircraft.php");
get_activity_history("*", " squitters", "squitters.php");

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

    <div style="text-align: center; font-size:26px; padding-top:20px;">
        <a href="index.php?month=<?php echo $prev_month; ?>&year=<?php echo $prev_month_year; ?>">
            <span class="its-img its-img-leftB"></span>
        </a>
        <?php echo $month_name; ?>
        <a href="index.php?month=<?php echo $next_month; ?>&year=<?php echo $next_month_year; ?>">
            <span class="its-img its-img-rightB"></span>
        </a>
    </div>

    <div style="text-align:center;">
        Receiver active between <?php echo $const->obs_earliest_date_short; ?> and
        <?php echo $const->obs_latest_date_short; ?>.
    </div>

    <div style="padding:4px;overflow-x:scroll;">
        <table class="dcf_calendar">
            <thead>
            <tr>
                <td>
                    <?php
                    print implode("</td><td>", ['Sun', 'Mon', 'Tue', 'Wed', 'Thur', 'Fri', 'Sat']);
                    ?>
                </td>
            </tr>
            </thead>
            <tbody>
            <tr>

                <?php
                for ($i = 0; $i < $day_offset; $i++) {
                    print "<td class='even'></td>";
                }

                $now_utc = time();
                $now_year = intval(date("Y", $now_utc));
                $now_mc = intval(date("n", $now_utc));
                $now_day = intval(date("j", $now_utc));
                for ($day = 1; $day <= $days_in_month; $day++) {
                    print "<td class='odd' style='position:relative;'>";
                    print "<div class=\"cal_day\">${day}</div><div class=\"cal_body\">";
                    $all_blank = true;
                    $output = "";
                    foreach ($byday[$day] as $s) {
                        if (strlen($s) > 0) $all_blank = false;
                        $output .= $s;
                    }
                    if ($all_blank) $output = "<div style='height:55px;'><span class='cal_type'>No data</span></div>";
                    print "{$output}</div></td>";
                    $day_offset++;
                    if ($day_offset == 7) {
                        $day_offset = 0;
                        print "</tr>";
                        if ($day < $days_in_month) print"<tr>";
                    }
                }

                if ($day_offset > 0) {
                    for ($day = $day_offset; $day < 7; $day++) {
                        print "<td class='even'></td>";
                    }
                    print "</tr>";
                }

                ?>
            </tbody>
        </table>
    </div>

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
