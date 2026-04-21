

create table tblPortfolioPlus (
	[ppid] int identity(1,1)
	, [GrantStatus] varchar(12)
	, [PhaseType] varchar(25)
	, [PhaseStatus] varchar(50)
	, [Grant] int
	, [LongTitle] nvarchar(255)
	, [ExternalRef] nvarchar(50) NULL
	, [PI] varchar(75)
	, [Location] varchar(50)
	, [Faculty] varchar(50)
	, [ResearchStart] date null
	, [ResearchEnd] date null
	, [OutlineDate] date null
	, [ApplicationDate] date null
	, [AwardDate] date null
	, [LeedsPrice] decimal(11,2)
	, ValidFrom DateTime default getdate()
	, ValidTo DateTime null
	, CreatedBy varchar(50) default suser_sname()
	CONSTRAINT PK_PortfolioPlus PRIMARY KEY ([ppid])
	)


