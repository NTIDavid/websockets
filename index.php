<?php
session_name("wsgame");
session_start();
?>
<!DOCTYPE html>
<html lang="sv">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=0.5, maximum-scale=1, user-scalable=0">
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
	<script src="ajax.js?r=<?php echo rand(0, 99999999); ?>"></script>
	<script src="js.js?r=<?php echo rand(0, 99999999); ?>"></script>
	<link rel="stylesheet" href="css.css?r=<?php echo rand(0, 99999999); ?>">
</head>
<body>
	<h1>ntikstad.com/tests/ws</h1>
	<!--<a href="logout.php">Logga ut</a><br>-->
	<p id="lat"></p>
	<p id="error"></p>
	<canvas></canvas>
</body>
</html>