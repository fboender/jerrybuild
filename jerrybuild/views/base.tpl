<!DOCTYPE html>
<html>
<head>
    <base href="/" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta charset="utf-8">
    <title>{{title or 'No title'}}</title>
    <meta name="description" content="">
    <meta name="author" content="">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="static/css/reset.css">
    <link rel="stylesheet" href="static/css/index.css">
    <link rel="stylesheet" href="static/font-awesome/css/font-awesome.min.css">
    % if get("reload_page", False):
        <meta http-equiv="refresh" content="5">
    % end
    <!--[if lt IE 9]>
    <script src="//cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.2/html5shiv.min.js"></script>
    <script src="//cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.min.js"></script>
    <![endif]-->
    <link rel="shortcut icon" href="">
</head>
<body>
    <header>
        <a href="/"><h1><span class="valign-helper"></span><img src="static/img/logo.png" alt="Jerrybuild" title="Jerrybuild" /></h1></a>
    </header>
    {{!base}}
    <footer>
        Jerrybuild v%%VERSION%%. &copy; 2016, Ferry Boender. Released under the <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GPLv3</a>. See <a href="https://github.com/fboender/jerrybuild">the github page</a> for more information.
    </footer>
</body>
</html>
