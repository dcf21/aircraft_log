<?php

$php_path = realpath(dirname(__FILE__));

require_once $php_path . "/utils.php";

class constants
{
    public $sitename;
    public $server;
    public $server_json;
    public $copyright;
    public $lastUpdate;
    public $path;
    public $rsyear, $rsmc, $rsday;

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
    }
}

$const = new constants();
