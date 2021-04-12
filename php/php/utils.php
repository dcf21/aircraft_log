<?php

class utils
{

    public static function is_cli()
    {
        return (!isset($_SERVER['SERVER_SOFTWARE']) &&
            (php_sapi_name() == 'cli' || (is_numeric($_SERVER['argc']) && $_SERVER['argc'] > 0)));
    }

    public static function dcf_sgn($num)
    {
        if ($num < 0) return -1;
        if ($num == 0) return 0;
        return 1;
    }

    public static function startsWith($haystack, $needle)
    {
        return $needle === "" || strrpos($haystack, $needle, -strlen($haystack)) !== FALSE;
    }

    public static function endsWith($haystack, $needle)
    {
        return $needle === "" || strpos($haystack, $needle, strlen($haystack) - strlen($needle)) !== FALSE;
    }

    public static function joinPaths()
    {
        $paths = array();

        foreach (func_get_args() as $arg) {
            if ($arg !== '') {
                $paths[] = $arg;
            }
        }

        return preg_replace('#/+#', '/', join('/', $paths));
    }

    public static function latString($l)
    {
        if ($l<0) return sprintf("%d&deg;S",-$l);
        else      return sprintf("%d&deg;N", $l);
    }

    public static function timeArithmetic($h,$m,$o)
    {
        $m+=$o;
        while ($m<  0) { $m+=60; $h-=1; }
        while ($m>=60) { $m-=60; $h+=1; }
        while ($h<  0) { $h+=24; }
        while ($h>=24) { $h-=24; }
        return sprintf("%02d:%02d",$h,$m);
    }

    public static function timeLongitude($h,$m,$o)
    {
        $longitude = ($h + $m/60 + $o/60)*360/24;
        while ($longitude >  180) $longitude -= 360;
        while ($longitude < -180) $longitude += 360;
        if ($longitude < 0) return sprintf("%d&deg;E",-$longitude);
        return sprintf("%d&deg;W",$longitude);
    }

    public static function timeArithStr($h0,$m0,$h1,$m1)
    {
        $t0 = $h0*60+$m0;
        $t1 = $h1*60+$m1;
        $d  = ($t1-$t0);
        while ($d<0    ) $d+=24*60;
        while ($d>24*60) $d-=24*60;
        $prep = ($d>12*60) ? "before" : "after";
        if ($d>12*60) $d=24*60-$d;
        $h  = floor($d/60);
        $m  = floor($d%60);
        $mp = ($m==1)?"":"s";
        if      ($h==0) return sprintf("%d minute%s %s",$m,$mp,$prep);
        else if ($h==1) return sprintf("1 hour and %d minute%s %s",$m,$mp,$prep);
        else            return sprintf("%d hours and %d minute%s %s",$h,$m,$mp,$prep);
    }


}
