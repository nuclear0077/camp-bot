/****** Object:  Table [dbo].[prefix_table_clients_bot]    Script Date: 09.05.2022 19:19:09 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[prefix_table_clients_bot](
	[User_id] [bigint] NOT NULL,
	[date_reg] [varchar](50) NULL,
	[F_name] [varchar](50) NULL,
	[L_name] [varchar](50) NULL,
	[Age] [int] NULL,
	[Gender] [varchar](50) NULL,
	[City] [varchar](50) NULL,
	[Is_active] [int] NOT NULL,
	[Department] [float] NULL,
	[Admin] [int] NOT NULL
) ON [PRIMARY]
GO


