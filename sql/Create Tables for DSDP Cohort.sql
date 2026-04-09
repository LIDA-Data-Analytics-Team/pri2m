/****************************************
[dbo].[tblDSDPCohort]
****************************************/
CREATE TABLE [dbo].[tblDSDPCohort](
	[DSDPCohortID] [int] IDENTITY(1,1) NOT NULL,
	[Cohort] varchar(25) NOT NULL,
	[ProjectNumber] [varchar](5) NOT NULL,
 CONSTRAINT [PK_DSDPCohort] PRIMARY KEY NONCLUSTERED 
(
	[DSDPCohortID] ASC
)WITH (STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, OPTIMIZE_FOR_SEQUENTIAL_KEY = OFF) ON [PRIMARY]
) ON [PRIMARY]
GO