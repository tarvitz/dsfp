#
# How to use:
# type '.\Fix-Checksums.ps1 .\DRAKS0005.sl2' into powershell
# obviously the path to the save file needs to point to an actual save file
#

param($file)

$filepath = join-path -resolve ( $MyInvocation.MyCommand.Path | split-path ) $file
$filebinary =  [System.IO.File]::ReadAllBytes( $filepath )

function extr {
 param( $source, $start, $length )
	$target = new-object byte[] $length
	[Array]::Copy($source,$start,$target,0,$length)
	return $target
}

function slot {
 param( $start, $allbytes )
	write-host -nonewline ( "Slot @ 0x{0:X}" -f $start )
	$md5 = new-object -TypeName System.Security.Cryptography.MD5CryptoServiceProvider

	# the existing checksums
	$first16 = (extr -source $allbytes -start $start -length 16)
	$last16 = (extr -source $allbytes -start ($start+393220) -length 16)

	# the secondary checksum must be calculated first,
	# because it is a part of the primary checksum
	# is it correct?
	$md5S = $md5.ComputeHash($allbytes,($start+20),393200) 
	$sExisting = [System.BitConverter]::ToString($last16)
	$sCalculated = [System.BitConverter]::ToString($md5S)
	if( $sExisting -ne $sCalculated )
	{
		write-host "`nExisting secondary checksum: $sExisting"
		write-host "                should be: $sCalculated"
		[Array]::Copy($md5S,0,$allbytes,($start+393220),16)
		write-host "                fixd."
	}

	# is the primary checksum correct?
	$md5P = $md5.ComputeHash($allbytes,($start+16),393220) 
	$pExisting = [System.BitConverter]::ToString($first16)
	$pCalculated = [System.BitConverter]::ToString($md5P)
	if( $pExisting -ne $pCalculated )
	{
		write-host "`nExisting primary checksum: $pExisting"
		write-host "                should be: $pCalculated"
		[Array]::Copy($md5P,0,$allbytes,$start,16)
		write-host "                fixd."
	}


	if( $pExisting -eq $pCalculated -and $sExisting -eq $sCalculated )
	{
		write-host " OK"
		return $true;
	}
	write-host ""
	return $false;
}

$start = 0x2C0
$count = 0
$needswrite = $false;
while($count -lt 10)
{
	$res = slot -start ($start+($count*0x60020)) -allbytes $filebinary
	if( !$res )
	{
		$needswrite = $true;
	}
	$count++;
}

if( $needswrite )
{
	[System.IO.File]::WriteAllBytes( "$filepath.fixd", $filebinary )
	write-host "Saved corrected file as $filepath.fixd"
}
