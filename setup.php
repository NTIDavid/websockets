<?php
session_name("wsgame");
session_start();
if(isset($_SESSION["user"])) {
	echo json_encode($_SESSION["user"]);
} else {
	if(isset($_GET["id"])) {
		$_SESSION["user"] = $_GET["id"];
		echo json_encode($_GET["id"]);
	} else {
		echo json_encode(false);
	}
}
?>