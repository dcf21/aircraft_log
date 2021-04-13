<?php

$php_path = realpath(dirname(__FILE__));

require_once $php_path . "/utils.php";

class constants
{
    public $sitename;
    public $server;
    public $copyright;
    public $lastUpdate;
    public $path;
    public $yearMin, $yearMax;
    public $obs_earliest, $obs_latest;
    public $obs_earliest_date, $obs_latest_date;
    public $obs_earliest_date_short, $obs_latest_date_short;

    public function __construct()
    {
        // Path to PHP modules directory
        $this->path = realpath(dirname(__FILE__));

        // Time we started execution
        $this->timeStart = microtime(True);

        // Set all calculations to work in UTC
        date_default_timezone_set("UTC");

        // SQL code used to fetch the current unix time
        $this->sql_unixtime = "UNIX_TIMESTAMP()";

        // List of names of the months
        $this->fullMonthNames = explode(" ", "x January February March April May June July August September October November December");
        $this->shortMonthNames = explode(" ", "x Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec");
        unset($this->shortMonthNames[0]);
        unset($this->fullMonthNames[0]);

        // Database connection details
        $this->mysqlProfile = trim(file_get_contents(
            utils::joinPaths($this->path, "../../../build/initdb/dbinfo/db_profile")));
        $this->mysqlLogin = file_get_contents(
            utils::joinPaths($this->path, "../../../build/initdb/dbinfo/db_profile_" . $this->mysqlProfile));
        $this->mysqlLoginLines = explode("\n", $this->mysqlLogin);
        $this->mysqlHost = $this->mysqlLoginLines[6];
        $this->mysqlUser = $this->mysqlLoginLines[0];
        $this->mysqlPassword = $this->mysqlLoginLines[1];
        $this->mysqlDB = $this->mysqlLoginLines[2];

        // Connect to database
        $this->db = new PDO("mysql:host=" . $this->mysqlHost . ";dbname=" . $this->mysqlDB, $this->mysqlUser,
            $this->mysqlPassword) or die ("Can't connect to SQL database.");
        $this->db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);

        // Fetch constants and ranges from database
        $stmt = $this->db->prepare("SELECT name,value FROM adsb_constants;");
        $stmt->execute([]);
        $result = $stmt->fetchAll(PDO::FETCH_ASSOC);
        foreach ($result as $item) $this->{$item['name']} = $item['value'];

        // Get time range of data
        $this->obs_earliest = 1618317941;
        $this->obs_latest = time();
        $stmt = $this->db->prepare("
SELECT MIN(generated_timestamp) AS t_min, MAX(generated_timestamp) AS t_max
FROM adsb_squitters;");
        $stmt->execute([]);
        $result = $stmt->fetchAll(PDO::FETCH_ASSOC);
        if (count($result)) {
            if ($result[0]['t_min'] > 0) {
                $this->obs_earliest = $result[0]['t_min'];
            }

            if ($result[0]['t_max'] > 0) {
                $this->obs_latest = $result[0]['t_max'];
            }
        }
        $this->yearMin = date("Y", $this->obs_earliest);
        $this->yearMax = date("Y", $this->obs_latest);

        $this->obs_earliest_date = date("d M Y - H:i", $this->obs_earliest);
        $this->obs_earliest_date_short = date("d M Y", $this->obs_earliest);

        $this->obs_latest_date = date("d M Y - H:i", $this->obs_latest);
        $this->obs_latest_date_short = date("d M Y", $this->obs_latest);
    }
}

$const = new constants();
