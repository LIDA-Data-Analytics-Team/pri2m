
/*
Set LASER flag on Grant where there exists a relationship with a project that is LASER = True
*/
update [dbo].[tblKristal]
set LASER = 1
where ValidTo is null
	and [KristalNumber] in (
		select [KristalNumber] 
		from [dbo].[tblProjectKristal] pk
		where pk.ValidTo is null
			and pk.[ProjectNumber] in (
				select [ProjectNumber] 
				from [dbo].[tblProject] 
				where ValidTo is null 
					and LASER = 1)
		)

/*
Set DSDP flag on Grant where there exists a relationship with a project that is Internship = True
*/
update [dbo].[tblKristal]
set DSDP = 1
where ValidTo is null
	and [KristalNumber] in (
		select [KristalNumber] 
		from [dbo].[tblProjectKristal] pk
		where pk.ValidTo is null
			and pk.[ProjectNumber] in (
				select [ProjectNumber] 
				from [dbo].[tblProject] 
				where ValidTo is null 
					and Internship = 1)
		)

/*
Set RIDM flag on Grant where there exists Note flag
*/
update [dbo].[tblKristal]
set RIDM = 1
where ValidTo is null
	and [KristalNumber] in (select [KristalNumber] from [dbo].[tblKristalNotes] where [KristalNote] in ('#RIS', 'RIDM', '#ridm' ))

/*
Set Community flag on Grant where there exists Note flag
*/
update [dbo].[tblKristal]
set Community = 1
where ValidTo is null
	and [KristalNumber] in (select [KristalNumber] from [dbo].[tblKristalNotes] where [KristalNote] in ('#C&P', 'C&P' ))


