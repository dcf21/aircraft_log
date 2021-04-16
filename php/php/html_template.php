<?php

class HTMLtemplate
{
    public static function breadcrumb($items, $area, $postbreadcrumb = null)
    {
        global $const;
        $server = $const->server;
        if (is_null($items)) return;
        if ($area == "about") {
            array_unshift($items, ["about.php", "About"]);
        }
        array_unshift($items, ["", "Home"]);
        ?>
        <table style="margin-top:8px;">
            <tr>
                <td class="snugtop" style="white-space:nowrap;">
                    <p class="smtext" style="padding:12px 0 6px 0;">
                        <?php
                        $firstItem = true;
                        foreach ($items as $arg) {
                            print '<span class="chevron_holder">';
                            if (!$firstItem) print '<span class="chevronsep">&nbsp;</span>';
                            print "<a class='chevron' href='{$server}{$arg[0]}'>{$arg[1]}</a></span>";
                            $firstItem = false;
                        }
                        ?>
                    </p></td>
                <?php if ($postbreadcrumb): ?>
                    <td style="padding-left:20px;vertical-align:middle;">
                        <span class="postchevron">
<?php
$first = true;
foreach ($postbreadcrumb as $c) {
    $cname = str_replace(" ", "&nbsp;", htmlentities($c[1], ENT_QUOTES));
    if (!$first) {
        print "&nbsp;| ";
    } else {
        $first = false;
    }
    print "<a href=\"{$server}{$c[0]}\">" . $cname . "</a>";
}
?>
                        </span>
                    </td>
                <?php endif; ?>
            </tr>
        </table>
        <?php
    }

    public static function require_html5()
    {
        ?>
        <!--[if lt IE 9]>
        <p class="smtext" style="background-color:#a00;color:white;border:1px solid #222;margin:16px 4px;padding:8px;">
            <b>
                You appear to be using an old web browser which may not be compatible with the interactive elements of
                this website. This page is compatible with most modern web browsers, including Chrome, Firefox, Safari
                and Internet Explorer 9+, but not with older versions of Internet Explorer.
            </b>
        </p>
        <![endif]-->
        <?php
    }

    public static function header($pageInfo)
    {
        global $const;
        if (!isset($pageInfo["breadcrumb"])) $pageInfo["breadcrumb"] = [];
        if (!isset($pageInfo["postbreadcrumb"])) $pageInfo["postbreadcrumb"] = null;
        $server = $const->server;
        $sitename = $const->sitename;

        header("Content-Security-Policy: frame-ancestors 'none'");
        header("X-Frame-Options: DENY");

        print<<<__HTML__
<!DOCTYPE html>
<html lang="en">
__HTML__;
        ?>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
            <meta http-equiv="x-ua-compatible" content="ie=edge">
            <meta name="description" content="<?php echo $pageInfo["pageDescription"]; ?>"/>
            <meta name="keywords"
                  content="photo gallery"/>
            <meta name="generator" content="Dominic Ford"/>
            <meta name="author" content="Dominic Ford"/>

            <title id="title1">
                <?php echo $pageInfo["pageTitle"]; ?>
            </title>

            <!--[if lt IE 9]>
            <script src="<?php echo $server; ?>vendor/html5shiv/dist/html5shiv.min.js" type="text/javascript"></script>
            <script src="<?php echo $server; ?>vendor/ExplorerCanvas/excanvas.js" type="text/javascript"></script>
            <![endif]-->

            <script>
                (function (i, s, o, g, r, a, m) {
                    i['GoogleAnalyticsObject'] = r;
                    i[r] = i[r] || function () {
                            (i[r].q = i[r].q || []).push(arguments)
                        }, i[r].l = 1 * new Date();
                    a = s.createElement(o),
                        m = s.getElementsByTagName(o)[0];
                    a.async = 1;
                    a.src = g;
                    m.parentNode.insertBefore(a, m)
                })(window, document, 'script', 'https://www.google-analytics.com/analytics.js', 'ga');

                ga('create', 'UA-22395429-1', 'auto');
                ga('send', 'pageview');

            </script>

            <script src="<?php echo $server; ?>vendor/jquery/dist/jquery.min.js" type="text/javascript"></script>

            <script src="<?php echo $server; ?>vendor/tether/dist/js/tether.min.js"></script>
            <link rel="stylesheet" href="<?php echo $server; ?>vendor/bootstrap/dist/css/bootstrap.min.css">
            <script src="<?php echo $server; ?>vendor/bootstrap/dist/js/bootstrap.min.js"></script>

            <script src="<?php echo $server; ?>vendor/jquery-ui/jquery-ui.min.js" type="text/javascript"></script>
            <link rel="stylesheet" type="text/css"
                  href="<?php echo $server; ?>vendor/jquery-ui/themes/ui-lightness/jquery-ui.min.css"/>
            <style type="text/css">
                .ui-slider-horizontal .ui-state-default {
                    background: url(<?php echo $server; ?>/images/sliderarrow.png) no-repeat;
                    width: 9px;
                    height: 20px;
                    border: 0 none;
                    margin-left: -4px;
                }

                .ui-slider-vertical .ui-state-default {
                    background: url(<?php echo $server; ?>/images/slidervarrow.png) no-repeat;
                    width: 20px;
                    height: 9px;
                    border: 0 none;
                    margin-left: -4px;
                }
            </style>

            <link
                    href='https://fonts.googleapis.com/css?family=Open+Sans:400,400italic,700,700italic&amp;subset=latin,greek'
                    rel='stylesheet' type='text/css'/>
            <link rel="stylesheet" href="<?php echo $server; ?>vendor/font-awesome/css/font-awesome.min.css">

            <?php if ((!isset($pageInfo["noPageFurniture"])) || (!$pageInfo["noPageFurniture"])): ?>
                <script type="text/javascript" id="cookiebanner"
                        src="<?php echo $server; ?>js/vendor/cookiebanner.js"
                        data-linkmsg="privacy policy"
                        data-moreinfo="<?php echo $server; ?>about_privacy.php"
                        data-message="<?php echo $sitename; ?> uses cookies to personalise content to your geographic location. By continuing to use this site you consent to our ">
                </script>
            <?php endif; ?>


            <link rel="stylesheet" type="text/css" href="<?php echo $server; ?>css/style.css" media="all"/>
            <link rel="stylesheet" type="text/css" href="<?php echo $server; ?>css/style-print.css" media="print"/>

            <script type="text/javascript">
                window.server = "<?php echo $server; ?>";
            </script>

            <script type="text/javascript" src="<?php echo $server; ?>js/dcford.min.js"></script>

            <?php if ($pageInfo["teaserImg"]): ?>
                <link rel="image_src" href="<?php echo $server . $pageInfo["teaserImg"]; ?>"
                      title="<?php echo $pageInfo["pageTitle"]; ?>"/>
                <meta property="og:image" content="<?php echo $server . $pageInfo["teaserImg"]; ?>"/>
            <?php endif; ?>

            <?php echo $pageInfo["cssextra"]; ?>
        </head>

        <?php echo "<body><div class=\"contentwrapper\">"; ?>

        <nav id="navbar-header" class="navbar navbar-dark bg-inverse navbar-fixed-top">
            <div class="container">
                <a class="navbar-brand" style="padding-right:25px;" href="<?php echo $server; ?>">
                    <i class="fa fa-home" aria-hidden="true"></i>
                </a>

                <ul class="nav navbar-nav">
                    <li class="nav-item">
                        <a class="nav-link" href="https://in-the-sky.org">
                            In-The-Sky.org
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="https://sciencedemos.org.uk">
                            Science Demos
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="https://hilltopviews.org.uk">
                            Hill Top Views
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="https://photos.dcford.org.uk">
                            Photography
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="http://pyxplot.org.uk">
                            Pyxplot
                        </a>
                    </li>
                </ul>
            </div>
        </nav>

        <?php
        print '<div class="mainpage container' .
            ((isset($pageInfo["fluid"]) && $pageInfo["fluid"]) ? "-fluid" : "") . '">';
        print '<div class="mainpane" style="padding-top:60px;">';
    }

    public function footer($pageInfo)
    {
        global $const;
        $server = $const->server;
        print "</div>"; // mainpane
        print "</div>"; // mainpane_container
        ?>

        <div class="footer">
            <div class="container">
                <div class="row">
                    <div class="col-md-5">
                        <p class="copyright">
                            <span style="font-size:15px;">
                            &copy; <a href="<?php echo $server; ?>about.php" rel="nofollow">Dominic
                                    Ford</a> 2016&ndash;<?php echo date("Y"); ?>.
                            </span>
                        </p>

                        <p class="copyright">
                            Our privacy policy is
                            <a href="<?php echo $server; ?>about_privacy.php" rel="nofollow">here</a>.<br/>
                            Last updated: <?php echo date("d M Y, H:i", $const->lastUpdate); ?> UTC<br/>
                            Website designed by
                            <span class="its-img its-img-email"
                                  style="height:14px;width:162px;vertical-align:middle;"></span>.<br/>
                        </p>
                    </div>
                    <div class="col-md-7">
                        <div style="display:inline-block;padding:16px;">
                            <?php $thisURI = urlencode($_SERVER["SERVER_NAME"] . $_SERVER["REQUEST_URI"]); ?>
                            <a href="https://validator.w3.org/nu/?doc=<?php echo $thisURI; ?>" rel="nofollow">
                                <div class="its-img its-img-vhtml" style="vertical-align:middle;"></div>
                            </a>
                            <a href="http://jigsaw.w3.org/css-validator/validator?uri=<?php echo $thisURI; ?>"
                               rel="nofollow">
                                <div class="its-img its-img-vcss" style="vertical-align:middle;"></div>
                            </a>
                        </div>
                    </div>
                </div>
            </div>

        </div>

        <?php
        print "</body></html>";
    }

    static public function showPager($result_count, $pageNum, $pageSize, $self_url)
    {
        $Npages = floor($result_count / $pageSize);
        $pageMin = max($pageNum - 5, 1);
        $pageMax = min($pageMin + 9, $Npages + 1);

        print "<div class='pager'>Page ";
        for ($p = $pageMin; $p <= $pageMax; $p++) {
            print "<span class='page'>";
            if ($p != $pageNum) print "<a href='{$self_url}&page={$p}'>";
            else print "<b>";
            print $p;
            if ($p != $pageNum) print "</a>";
            else print "</b>";
            print "</span>";
        }
        print "</div>";
    }

    static public function titleProcess($input)
    {
        return ucfirst(str_replace("_", " ", $input));
    }
}

$pageTemplate = new HTMLtemplate();
