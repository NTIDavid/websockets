<?php
session_name("wsgame");
session_start();
?>
<!DOCTYPE html>
<html lang="sv">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Websockets</title>
	<script>
var player = <?php
if(isset($_SESSION["user"])) {
	echo $_SESSION["user"];
} else {
	echo "null";
}
?>;
	</script>
	<script src="ajax.js"></script>
	<script src="js.js"></script>
	<link rel="stylesheet" href="css.css">
</head>
<body>
	<label for="autopilot">Autopilot</label> <input type="checkbox" id="autopilot">
	<a href="logout.php">Logga ut</a><br>
	<p id="lat"></p>
	<p id="error"></p>
	<canvas></canvas>
	<p id="log"></p>
</body>
</html>